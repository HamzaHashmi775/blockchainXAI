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
