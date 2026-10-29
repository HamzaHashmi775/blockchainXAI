import numpy as np
import pytest

from evaluation.stats import (checkpoint_verdict, describe, friedman, holm, paired_comparison,
                              rank_biserial, relative_improvement)


def test_describe():
    d = describe([1.0, 2.0, 3.0, 4.0, 5.0])
    assert d["mean"] == 3.0 and d["sd"] == pytest.approx(np.sqrt(2.5))
    assert d["ci_low"] == pytest.approx(3 - 2.7764 * np.sqrt(2.5 / 5), abs=1e-3)
    assert np.isnan(describe([1.0])["sd"])


def test_relative_improvement():
    assert relative_improvement(1.2, 1.0) == pytest.approx(0.2)
    assert relative_improvement(-0.5, -1.0) == pytest.approx(0.5)
    assert np.isnan(relative_improvement(1.0, 0.0))


def test_holm_matches_hand_computation():
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5, 0.9]) == pytest.approx([1.0, 1.0])
    out = holm([0.01, np.nan, 0.02])
    assert out[0] == pytest.approx(0.02) and np.isnan(out[1]) and out[2] == pytest.approx(0.02)


def test_rank_biserial_extremes():
    assert rank_biserial([1, 2, 3]) == 1.0
    assert rank_biserial([-1, -2, -3]) == -1.0
    assert rank_biserial([1, -1]) == 0.0
    assert np.isnan(rank_biserial([0, 0]))


def test_paired_comparison_t_test_branch():
    rng = np.random.default_rng(1)
    control = rng.normal(0.5, 0.05, 10)
    treatment = control + rng.normal(0.1, 0.02, 10)
    res = paired_comparison(treatment, control)
    assert res["test"] == "paired t-test" and res["p_value"] < 0.001
    assert res["effect_size_name"] == "cohen_dz" and res["effect_size"] > 1
    assert res["ci_low"] < res["mean_difference"] < res["ci_high"]


def test_paired_comparison_wilcoxon_branch():
    control = np.zeros(10)
    treatment = np.array([0.01] * 9 + [5.0])          # heavily non-normal differences
    res = paired_comparison(treatment, control)
    assert res["test"] == "Wilcoxon signed-rank"
    assert res["effect_size"] == 1.0 and res["ci_method"] == "percentile bootstrap"


def test_paired_comparison_constant_difference():
    res = paired_comparison(np.ones(10), np.zeros(10))
    assert res["test"].startswith("none") and np.isnan(res["p_value"])
    same = paired_comparison(np.ones(10), np.ones(10))
    assert same["p_value"] == 1.0 and same["mean_difference"] == 0.0


def test_friedman():
    rng = np.random.default_rng(0)
    base = rng.normal(size=10)
    res = friedman([base, base + 1, base + 2])
    assert res["p_value"] < 0.01
    assert friedman([base, base, base])["p_value"] == 1.0


def test_checkpoint_verdict_rule():
    better = {"mean_difference": 0.2, "relative_improvement": 0.4}
    tiny = {"mean_difference": 0.001, "relative_improvement": 0.01}
    worse = {"mean_difference": -0.2, "relative_improvement": -0.4}
    assert checkpoint_verdict(better, 0.01, higher_is_better=True) == "improved"
    assert checkpoint_verdict(better, 0.20, higher_is_better=True) == "negligible"
    assert checkpoint_verdict(tiny, 0.01, higher_is_better=True) == "negligible"
    assert checkpoint_verdict(worse, 0.01, higher_is_better=True) == "worse"
    assert checkpoint_verdict(worse, 0.01, higher_is_better=False) == "improved"
    assert checkpoint_verdict(better, float("nan"), higher_is_better=True) == "negligible"


def _cross_domain_module():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "statistics" / "analyze_cross_domain.py"
    spec = importlib.util.spec_from_file_location("analyze_cross_domain", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_summaries(folder, verdicts):
    import json

    def cmp(verdict):
        return {"mean_control": 0.5, "mean_treatment": 0.6, "mean_difference": 0.1,
                "ci_low": 0.05, "ci_high": 0.15, "relative_improvement": 0.2,
                "p_value": 0.01, "p_holm": 0.02, "test": "paired t-test", "verdict": verdict}

    for domain, by_outcome in verdicts.items():
        comparisons = {c: {o: cmp(by_outcome.get(o)) for o in
                           ("fidelity", "evidence_support", "manipulation",
                            "collective_accuracy", "manipulation_success")}
                       for c in ("proposed_vs_baseline", "ablation_vs_baseline")}
        main = {"n_seeds": 10, "comparisons": comparisons}
        (folder / f"{domain}_main.json").write_text(json.dumps(main))
        (folder / f"{domain}_llm.json").write_text(json.dumps({"main": main}))


def test_cross_domain_h6_compares_verdicts_and_never_pools(tmp_path):
    module = _cross_domain_module()
    _write_summaries(tmp_path, {
        "pharma": {"fidelity": "improved", "evidence_support": "improved",
                   "manipulation": "improved"},
        "energy": {"fidelity": "negligible", "evidence_support": "improved",
                   "manipulation": "improved"}})
    res = module.analyse(tmp_path)
    c = res["arms"]["classical"]["comparisons"]["proposed_vs_baseline"]
    assert c["h6_holds_for"] == ["evidence_support", "manipulation"]
    assert c["h6"]["fidelity"] == {"verdicts": {"pharma": "improved", "energy": "negligible"},
                                   "same_verdict": False}
    # secondary outcomes are reported but carry no H6 verdict
    assert "collective_accuracy" in c["outcomes"] and "collective_accuracy" not in c["h6"]
    assert "H6 holds for: evidence_support, manipulation (2 of 3)" in module.to_markdown(res)


def test_cross_domain_refuses_a_missing_verdict(tmp_path):
    module = _cross_domain_module()
    _write_summaries(tmp_path, {
        "pharma": {"fidelity": "improved", "evidence_support": "improved",
                   "manipulation": "improved"},
        "energy": {"fidelity": "improved", "evidence_support": "improved"}})
    with pytest.raises(ValueError, match="verdict missing"):
        module.analyse(tmp_path)


def test_sensitivity_robustness_ignores_exploratory_values(tmp_path):
    import importlib.util
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "statistics" / "summarize_sensitivity.py"
    spec = importlib.util.spec_from_file_location("summarize_sensitivity", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def comp(verdict):
        return {"verdict": verdict, "relative_improvement": 0.1}

    main = {"comparisons": {"proposed_vs_baseline": {
        "fidelity": comp("improved"), "evidence_support": comp("negligible"),
        "manipulation": comp("improved")}}}
    (tmp_path / "pharma_main.json").write_text(json.dumps(main))
    (tmp_path / "energy_main.json").write_text(json.dumps(main))
    by_value = {
        "0.5": {"proposed_vs_baseline": main["comparisons"]["proposed_vs_baseline"]},
        "0.9": {"proposed_vs_baseline": {"fidelity": comp("worse"),
                                         "evidence_support": comp("negligible"),
                                         "manipulation": comp("improved")}}}
    (tmp_path / "pharma_sensitivity_omega.json").write_text(json.dumps(
        {"parameter": "game.omega", "exploratory_values": ["0.9"], "by_value": by_value}))
    (tmp_path / "energy_sensitivity_omega.json").write_text(json.dumps(
        {"parameter": "game.omega", "exploratory_values": [], "by_value": by_value}))
    res = module.analyse(tmp_path)
    assert res["runs"]["pharma_sensitivity_omega"]["robust"]["fidelity"] is True
    assert res["runs"]["energy_sensitivity_omega"]["robust"]["fidelity"] is False
    assert "pharma_sensitivity_beta" in res["missing"]
