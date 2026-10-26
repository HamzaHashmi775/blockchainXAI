"""Sensitivity analysis: one parameter varied at a time (protocol section 7).

    python statistics/analyze_sensitivity.py --name energy_sensitivity_omega

Reads results/raw/<name>/seed_*.json; writes results/summaries/<name>.json and
tables/<name>.md.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.stats import checkpoint_verdict, describe, holm, paired_comparison  # noqa: E402

METRICS = ("fidelity", "evidence_support", "manipulation", "collective_accuracy",
           "manipulation_success")
CONFIRMATORY = ("fidelity", "evidence_support", "manipulation")


def analyse(name):
    folder = ROOT / "results" / "raw" / name
    manifest = json.loads((folder / "manifest.json").read_text())
    if manifest["status"] != "completed":
        raise SystemExit(f"{folder} has no completed run")
    seeds = manifest["seeds"]
    sens = manifest["config"]["sensitivity"]
    runs = {s: json.loads((folder / f"seed_{s}.json").read_text()) for s in seeds}
    values = list(runs[seeds[0]]["values"])
    systems = list(runs[seeds[0]]["values"][values[0]])
    out = {"name": name, "parameter": sens["parameter"], "values": values, "seeds": seeds,
           "exploratory_values": [str(v) for v in sens.get("exploratory_values", [])],
           "by_value": {}}
    for value in values:
        def series(system, metric):
            return np.array([runs[s]["values"][value][system]["metrics"][metric] for s in seeds])

        entry = {"descriptive": {m: {sy: describe(series(sy, m)) for sy in systems}
                                 for m in METRICS},
                 "honest_share": {sy: describe([runs[s]["values"][value][sy]["metrics"]
                                                ["strategy_share"]["honest"] for s in seeds])
                                  for sy in systems}}
        if {"proposed", "baseline"} <= set(systems):
            comp = {m: paired_comparison(series("proposed", m), series("baseline", m))
                    for m in METRICS}
            for m, p in zip(CONFIRMATORY, holm([comp[m]["p_value"] for m in CONFIRMATORY])):
                comp[m]["p_holm"] = float(p)
                comp[m]["verdict"] = checkpoint_verdict(comp[m], p, m != "manipulation")
            entry["proposed_vs_baseline"] = comp
        deviation = {}
        for system in systems:
            tables = [runs[s]["values"][value][system]["unilateral_deviation_payoff"] for s in seeds]
            agents = list(tables[0])
            strategies = list(tables[0][agents[0]])
            per_agent = {}
            for agent in agents:
                mean = {st: float(np.mean([t[agent][st] for t in tables])) for st in strategies}
                best_dev = max((st for st in strategies if st != "honest"), key=lambda st: mean[st])
                per_agent[agent] = {
                    "honest": mean["honest"], "best_deviation": best_dev,
                    "best_deviation_payoff": mean[best_dev],
                    "gain_from_deviating": mean[best_dev] - mean["honest"],
                    "honest_best_in_n_seeds": int(sum(
                        max(strategies, key=lambda st: t[agent][st]) == "honest" for t in tables))}
            deviation[system] = per_agent
        entry["unilateral_deviation"] = deviation
        entry["agents_for_whom_honest_is_best"] = {
            sy: int(sum(a["gain_from_deviating"] <= 0 for a in deviation[sy].values()))
            for sy in systems}
        out["by_value"][value] = entry
    return out


def to_markdown(res):
    lines = [f"# Sensitivity: {res['parameter']}", "",
             f"n = {len(res['seeds'])} seeds; mean ± SD. Exploratory (not pre-declared) values: "
             f"{res['exploratory_values'] or 'none'}.", ""]
    systems = list(next(iter(res["by_value"].values()))["honest_share"])
    for metric in METRICS + ("honest_share",):
        lines += [f"## {metric}", "", "| Value | " + " | ".join(systems) + " |",
                  "|---|" + "---|" * len(systems)]
        for value, entry in res["by_value"].items():
            source = entry["honest_share"] if metric == "honest_share" else entry["descriptive"][metric]
            lines.append(f"| {value} | " + " | ".join(
                f"{source[sy]['mean']:.3f} ± {source[sy]['sd']:.3f}" for sy in systems) + " |")
        lines.append("")
    lines += ["## Proposed − baseline", "",
              "| Value | Metric | Δ | 95% CI | Rel. | test | p | p (Holm) | Verdict |",
              "|---|---|---|---|---|---|---|---|---|"]
    for value, entry in res["by_value"].items():
        for metric in CONFIRMATORY:
            c = entry["proposed_vs_baseline"][metric]
            lines.append(f"| {value} | {metric} | {c['mean_difference']:+.3f} | "
                         f"[{c['ci_low']:+.3f}, {c['ci_high']:+.3f}] | "
                         f"{c['relative_improvement']:+.1%} | {c['test']} | {c['p_value']:.4f} | "
                         f"{c['p_holm']:.4f} | {c['verdict']} |")
    lines += ["", "## Unilateral deviation from all-honest: gain of the best deviation "
              "(positive = deviating pays)", "",
              "| Value | System | Agent | honest payoff | best deviation | gain | honest best in seeds |",
              "|---|---|---|---|---|---|---|"]
    for value, entry in res["by_value"].items():
        for system, agents in entry["unilateral_deviation"].items():
            for agent, row in agents.items():
                lines.append(f"| {value} | {system} | {agent} | {row['honest']:.3f} | "
                             f"{row['best_deviation']} | {row['gain_from_deviating']:+.3f} | "
                             f"{row['honest_best_in_n_seeds']}/{len(res['seeds'])} |")
    lines += ["", "Agents (of 5) for whom honest is the best unilateral response:"]
    for value, entry in res["by_value"].items():
        lines.append(f"- {value}: {entry['agents_for_whom_honest_is_best']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="energy_sensitivity_omega")
    args = parser.parse_args()
    result = analyse(args.name)
    (ROOT / "results" / "summaries" / f"{args.name}.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    (ROOT / "tables" / f"{args.name}.md").write_text(to_markdown(result), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(to_markdown(result))
