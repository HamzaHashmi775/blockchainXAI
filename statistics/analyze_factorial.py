"""2x2 wording x payoff design for LLM agents (protocol amendment 7).

    python statistics/analyze_factorial.py [--domain pharma|energy]

Cells (omega 0.5, seeds 0-4, audit checks shown in the history in all four):
A = baseline wording, baseline payoff; B = proposed wording, baseline payoff;
C = proposed wording, proposed payoff (all three from results/raw/<domain>_llm_prompt_control);
D = baseline wording, proposed payoff (results/raw/<domain>_llm_prompt_control_d, run in a
later Kaggle session). Writes results/summaries/<domain>_llm_factorial.json and
tables/<domain>_llm_factorial.md. Added, post hoc experiment: pharma is amendment 7, the
energy replication amendment 8 (which also fixes the replication rule below).

Calibration: stated confidence is compared with whether the agent's own vote was the
reference-best option (Brier score; mean confidence minus share correct). This is the
target against which "lower confidence" can be called better or worse calibrated.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "statistics"))

from analyze_llm import _get, load  # noqa: E402
from evaluation.stats import checkpoint_verdict, describe, holm, paired_comparison  # noqa: E402

SYSTEMS = {"A": "baseline_shown", "B": "prompt_only", "C": "proposed", "D": "payoff_only"}
AMENDMENT = {"pharma": 7, "energy": 8}


def cells(domain):
    """{cell: (run, system)}; A-C share one run, D is a separate run."""
    return {c: (f"{domain}_llm_prompt_control" + ("_d" if c == "D" else ""), system)
            for c, system in SYSTEMS.items()}


CELLS = cells("pharma")
PRIMARY = "mean_confidence"
METRICS = {"mean_confidence": ("behaviour", "mean_confidence"),
           "confidence_inflation": ("behaviour", "confidence_inflation"),
           "votes_against_tool": ("behaviour", "votes_against_tool"),
           "manipulation": ("manipulation",), "fidelity": ("fidelity",),
           "evidence_support": ("evidence_support",),
           "collective_accuracy": ("collective_accuracy",)}
CALIBRATION = ("brier", "overconfidence", "share_votes_correct")
VERDICT = {"improved": "lower", "worse": "higher", "negligible": "no detectable effect"}
# pre-declared bound for describing D - A: its 95 % CI lies within +-10 % of the size of
# the wording effect B - A
BOUND_SHARE = 0.10


def calibration(rounds):
    """Confidence of each agent's report against whether its vote was reference-best."""
    votes = np.asarray(rounds["votes"])
    conf = np.asarray(rounds["confidence"], dtype=float)
    correct = (votes == np.asarray(rounds["reference"])[:, None]).astype(float)
    return {"brier": float(np.mean((conf - correct) ** 2)),
            "overconfidence": float(conf.mean() - correct.mean()),
            "share_votes_correct": float(correct.mean())}


def cell_series(runs, seeds, metric, domain="pharma"):
    """{cell: array over seeds} for a metric or a calibration quantity."""
    out = {}
    for cell, (run, system) in cells(domain).items():
        values = []
        for s in seeds:
            data = runs[run][s]["systems"][system]
            values.append(calibration(data["rounds"])[metric] if metric in CALIBRATION
                          else _get(data["metrics"], METRICS[metric]))
        out[cell] = np.array(values, dtype=float)
    return out


def analyse(runs, domain="pharma"):
    names = cells(domain)
    seeds = sorted(set(runs[names["A"][0]]) & set(runs[names["D"][0]]))
    out = {"seeds": seeds, "n_seeds": len(seeds), "descriptive": {}, "effects": {},
           "simple_contrasts": {}}
    for metric in (*METRICS, *CALIBRATION):
        x = cell_series(runs, seeds, metric, domain)
        out["descriptive"][metric] = {c: describe(v) for c, v in x.items()}
        # factorial effects as paired comparisons over seeds
        effects = {
            "wording (main effect)": ((x["B"] + x["C"]) / 2, (x["A"] + x["D"]) / 2),
            "payoff (main effect)": ((x["D"] + x["C"]) / 2, (x["A"] + x["B"]) / 2),
            "interaction": (x["C"] - x["D"], x["B"] - x["A"]),
        }
        out["effects"][metric] = {k: paired_comparison(t, c) for k, (t, c) in effects.items()}
        out["simple_contrasts"][metric] = {
            "D_vs_A (payoff, baseline wording)": paired_comparison(x["D"], x["A"]),
            "C_vs_B (payoff, proposed wording)": paired_comparison(x["C"], x["B"]),
            "B_vs_A (wording, baseline payoff)": paired_comparison(x["B"], x["A"]),
            "C_vs_D (wording, proposed payoff)": paired_comparison(x["C"], x["D"])}
    # confirmatory family of this amendment: the three factorial effects on the primary outcome
    primary = out["effects"][PRIMARY]
    for name, p_adj in zip(primary, holm([primary[k]["p_value"] for k in primary])):
        primary[name]["p_holm"] = float(p_adj)
        primary[name]["verdict"] = (VERDICT[checkpoint_verdict(primary[name], p_adj, False)]
                                    if name != "interaction" else
                                    ("detected" if p_adj < 0.05 else "not detected"))
    d_a = out["simple_contrasts"][PRIMARY]["D_vs_A (payoff, baseline wording)"]
    b_a = out["simple_contrasts"][PRIMARY]["B_vs_A (wording, baseline payoff)"]
    bound = BOUND_SHARE * abs(b_a["mean_difference"])
    out["d_vs_a_bound"] = {
        "bound": bound, "ci": [d_a["ci_low"], d_a["ci_high"]],
        "within_bound": bool(-bound < d_a["ci_low"] and d_a["ci_high"] < bound)}
    calls = [runs[run][s]["systems"][system]["metrics"]["calls"] for run, system in
             names.values() for s in seeds]
    out["calls"] = {k: int(sum(c[k] for c in calls))
                    for k in ("total", "unusable_replies", "reports_replaced_by_tool_report")}
    if domain != "pharma":
        out["domain"] = domain
        out["replication"] = replication(out)
    return out


def replication(res):
    """Amendment 8, fixed before the energy run: the pharma pattern replicates if the
    wording main effect is 'lower', the payoff main effect is 'no detectable effect' and the
    CI of D - A lies within the pre-declared bound; otherwise each part not met is named."""
    primary = res["effects"][PRIMARY]
    parts = {"wording main effect lower":
             primary["wording (main effect)"]["verdict"] == "lower",
             "payoff main effect not detected":
             primary["payoff (main effect)"]["verdict"] == "no detectable effect",
             "D - A within the bound": res["d_vs_a_bound"]["within_bound"]}
    unmet = [k for k, ok in parts.items() if not ok]
    return {"parts": parts, "replicated": not unmet,
            "reading": ("the pharma pattern replicates" if not unmet else
                        "the pharma pattern does not replicate; not met: " + "; ".join(unmet))}


def checks_against_main_run(runs, domain, seeds):
    """Descriptive: A and C against the baseline and proposed systems of the amendment-4
    main run of the same domain (same seeds and rounds; GPU runs at temperature 0 are not
    bit-exact)."""
    original = load(f"{domain}_llm_main")
    if not original:
        return None
    run = cells(domain)["A"][0]
    out = {}
    for cell, system in (("C", "proposed"), ("A", "baseline")):
        out[f"{cell}_vs_original_{system}"] = {m: paired_comparison(
            np.array([_get(runs[run][s]["systems"][SYSTEMS[cell]]["metrics"], METRICS[m])
                      for s in seeds], dtype=float),
            np.array([_get(original[s]["systems"][system]["metrics"], METRICS[m])
                      for s in seeds], dtype=float)) for m in ("mean_confidence", "fidelity")}
    return out


def calibration_of_main_runs():
    """Descriptive: the same calibration quantities for the amendment-4 main runs."""
    out = {}
    for run in ("pharma_llm_main", "energy_llm_main", "pharma_llm_main_w075"):
        data = load(run)
        if not data:
            continue
        out[run] = {}
        for system in ("baseline", "proposed"):
            per_seed = [calibration(data[s]["systems"][system]["rounds"]) for s in sorted(data)]
            out[run][system] = {k: describe([p[k] for p in per_seed]) for k in CALIBRATION}
        out[run]["brier_proposed_vs_baseline"] = paired_comparison(
            np.array([calibration(data[s]["systems"]["proposed"]["rounds"])["brier"]
                      for s in sorted(data)]),
            np.array([calibration(data[s]["systems"]["baseline"]["rounds"])["brier"]
                      for s in sorted(data)]))
    return out


def _cell(d):
    return f"{d['mean']:.3f} ± {d['sd']:.3f}"


def to_markdown(res):
    domain = res.get("domain", "pharma")
    lines = [
        f"# 2×2 wording × payoff ({domain}, LLM agents) — added, post hoc experiment",
        "",
        f"n = {res['n_seeds']} paired seeds; ω = 0.5; audit checks shown in all cells. "
        "A, B, C from one Kaggle session; D from a later session "
        f"(amendment {AMENDMENT[domain]}). "
        f"Model calls: {res['calls']['total']}; unusable replies: "
        f"{res['calls']['unusable_replies']}.",
        "",
        "| Outcome | A (base words, base pay) | B (prop. words, base pay) | "
        "C (prop. words, prop. pay) | D (base words, prop. pay) |",
        "|---|---|---|---|---|",
    ]
    for m, by in res["descriptive"].items():
        lines.append(f"| {m} | {_cell(by['A'])} | {_cell(by['B'])} | {_cell(by['C'])} | "
                     f"{_cell(by['D'])} |")
    lines += ["", f"## Factorial effects on {PRIMARY} (confirmatory family of amendment "
              f"{AMENDMENT[domain]})", "",
              "| Effect | Δ | 95% CI | Test | p | p (Holm) | Verdict |",
              "|---|---|---|---|---|---|---|"]
    for name, c in res["effects"][PRIMARY].items():
        lines.append(f"| {name} | {c['mean_difference']:+.3f} | [{c['ci_low']:+.3f}, "
                     f"{c['ci_high']:+.3f}] | {c['test']} | {c['p_value']:.4f} | "
                     f"{c['p_holm']:.4f} | {c['verdict']} |")
    b = res["d_vs_a_bound"]
    lines += ["", f"D − A on {PRIMARY}: 95% CI [{b['ci'][0]:+.3f}, {b['ci'][1]:+.3f}]; "
              f"pre-declared bound ±{b['bound']:.3f} (10 % of the wording effect B − A): "
              + ("CI within the bound" if b["within_bound"] else "CI not within the bound")
              + "."]
    if "replication" in res:
        lines += ["", "Replication of the pharma pattern (rule of amendment 8): **"
                  + res["replication"]["reading"] + "**."]
    if res.get("checks_against_main_run"):
        lines += ["", f"Descriptive checks against {domain}_llm_main (same seeds and rounds):"]
        for name, by in res["checks_against_main_run"].items():
            lines.append(f"- {name}: " + "; ".join(
                f"{m} Δ {c['mean_difference']:+.3f} (p {c['p_value']:.3f})"
                for m, c in by.items()))
    lines += ["",
              "## Simple contrasts and factorial effects, all outcomes (secondary, unadjusted)",
              "", "| Outcome | Contrast | Δ | 95% CI | p |", "|---|---|---|---|---|"]
    for m in res["simple_contrasts"]:
        for name, c in {**res["simple_contrasts"][m], **res["effects"][m]}.items():
            lines.append(f"| {m} | {name} | {c['mean_difference']:+.3f} | "
                         f"[{c['ci_low']:+.3f}, {c['ci_high']:+.3f}] | {c['p_value']:.4f} |")
    if res.get("calibration_main_runs"):
        lines += ["", "## Calibration of the amendment-4 main runs (descriptive)", "",
                  "| Run | System | Brier | Overconfidence | Share of votes correct |",
                  "|---|---|---|---|---|"]
        for run, by in res["calibration_main_runs"].items():
            for system in ("baseline", "proposed"):
                d = by[system]
                lines.append(f"| {run} | {system} | {_cell(d['brier'])} | "
                             f"{_cell(d['overconfidence'])} | "
                             f"{_cell(d['share_votes_correct'])} |")
            c = by["brier_proposed_vs_baseline"]
            lines.append(f"| {run} | Δ Brier (proposed − baseline) | "
                         f"{c['mean_difference']:+.3f} [{c['ci_low']:+.3f}, "
                         f"{c['ci_high']:+.3f}], p {c['p_value']:.4f} | | |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="2x2 wording x payoff analysis")
    parser.add_argument("--domain", choices=sorted(AMENDMENT), default="pharma")
    domain = parser.parse_args(argv).domain
    runs = {run: load(run) for run, _ in cells(domain).values()}
    missing = [r for r, d in runs.items() if not d]
    if missing:
        raise SystemExit(f"no results in results/raw/ for {missing}")
    res = analyse(runs, domain)
    if domain == "pharma":
        res["calibration_main_runs"] = calibration_of_main_runs()
    else:
        res["checks_against_main_run"] = checks_against_main_run(runs, domain, res["seeds"])
    (ROOT / "results" / "summaries" / f"{domain}_llm_factorial.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8")
    text = to_markdown(res)
    (ROOT / "tables" / f"{domain}_llm_factorial.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
