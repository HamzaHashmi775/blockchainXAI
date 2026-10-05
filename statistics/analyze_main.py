"""Main-experiment analysis: baseline vs ablation vs proposed (protocol section 9).

    python statistics/analyze_main.py --domain energy

Reads results/raw/<domain>_{baseline,ablation,proposed}/seed_*.json and writes
results/summaries/<domain>_main.json and tables/<domain>_main.md. Every number
comes from the saved per-seed results.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.stats import checkpoint_verdict, describe, holm, paired_comparison  # noqa: E402

SYSTEMS = ("baseline", "ablation", "proposed")
# metric -> higher is better
CONFIRMATORY = {"fidelity": True, "evidence_support": True, "manipulation": False}
SECONDARY = {"collective_accuracy": True, "collective_utility": True, "decision_quality": True,
             "manipulation_success": False, "consistency": True}
STRATEGIES = ("honest", "strategic", "manipulative")


def load(domain, system):
    folder = ROOT / "results" / "raw" / f"{domain}_{system}"
    manifest = json.loads((folder / "manifest.json").read_text())
    if manifest["status"] != "completed":
        raise SystemExit(f"{folder} has no completed run")
    return {seed: json.loads((folder / f"seed_{seed}.json").read_text())
            for seed in manifest["seeds"]}


def analyse(domain):
    runs = {s: load(domain, s) for s in SYSTEMS}
    seeds = sorted(runs["baseline"])
    if any(sorted(runs[s]) != seeds for s in SYSTEMS):
        raise SystemExit("systems were not run on identical seeds; paired analysis impossible")

    def series(system, metric):
        return np.array([runs[system][seed]["metrics"][metric] for seed in seeds])

    metrics = {**CONFIRMATORY, **SECONDARY}
    out = {"domain": domain, "seeds": seeds, "n_seeds": len(seeds),
           "descriptive": {m: {s: describe(series(s, m)) for s in SYSTEMS} for m in metrics},
           "strategy_share": {s: {st: describe([runs[s][seed]["metrics"]["strategy_share"][st]
                                                for seed in seeds]) for st in STRATEGIES}
                              for s in SYSTEMS},
           "comparisons": {}}
    for treatment in ("proposed", "ablation"):
        comp = {m: paired_comparison(series(treatment, m), series("baseline", m)) for m in metrics}
        adjusted = holm([comp[m]["p_value"] for m in CONFIRMATORY])
        for m, p_adj in zip(CONFIRMATORY, adjusted):
            comp[m]["p_holm"] = float(p_adj)
            comp[m]["verdict"] = checkpoint_verdict(comp[m], p_adj, CONFIRMATORY[m])
        out["comparisons"][f"{treatment}_vs_baseline"] = comp

    # unilateral deviations from the all-honest profile: mean payoff per strategy
    deviation = {}
    for system in SYSTEMS:
        agents = runs[system][seeds[0]]["unilateral_deviation_payoff"].keys()
        deviation[system] = {}
        for agent in agents:
            row = {st: float(np.mean([runs[system][seed]["unilateral_deviation_payoff"][agent][st]
                                      for seed in seeds])) for st in STRATEGIES}
            row["best_response"] = max(STRATEGIES, key=lambda st: row[st])
            row["honest_is_best_in_n_seeds"] = int(sum(
                max(STRATEGIES, key=lambda st: runs[system][seed]["unilateral_deviation_payoff"]
                    [agent][st]) == "honest" for seed in seeds))
            deviation[system][agent] = row
    out["unilateral_deviation"] = deviation
    out["model_val_accuracy"] = {
        agent: describe([runs["baseline"][seed]["model_val_accuracy"][agent] for seed in seeds])
        for agent in runs["baseline"][seeds[0]]["model_val_accuracy"]}

    verdicts = [out["comparisons"]["proposed_vs_baseline"][m]["verdict"] for m in CONFIRMATORY]
    out["checkpoint"] = {
        "verdicts": dict(zip(CONFIRMATORY, verdicts)),
        "continue": bool("improved" in verdicts and "worse" not in verdicts)}
    return out


def to_markdown(res):
    lines = [f"# {res['domain'].capitalize()} — baseline vs ablation vs proposed",
             "", f"n = {res['n_seeds']} paired seeds; mean ± SD over seeds; metrics averaged over "
             "agents and the evaluation window.", "",
             "| Metric | Baseline | Ablation | Proposed |", "|---|---|---|---|"]
    for metric, by_system in res["descriptive"].items():
        cells = [f"{by_system[s]['mean']:.3f} ± {by_system[s]['sd']:.3f}" for s in SYSTEMS]
        lines.append(f"| {metric} | " + " | ".join(cells) + " |")
    for name, comp in res["comparisons"].items():
        lines += ["", f"## {name.replace('_', ' ')}", "",
                  "| Metric | Δ mean | 95% CI | Rel. impr. | Test | p | p (Holm) | Effect | Verdict |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for metric, c in comp.items():
            lines.append(
                f"| {metric} | {c['mean_difference']:+.3f} | [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}] "
                f"| {c['relative_improvement']:+.1%} | {c['test']} | {c['p_value']:.4f} "
                f"| {c.get('p_holm', float('nan')):.4f} | {c['effect_size_name']} = "
                f"{c['effect_size']:.2f} | {c.get('verdict', '—')} |")
    lines += ["", "## Learned strategy shares (evaluation window)", "",
              "| System | honest | strategic | manipulative |", "|---|---|---|---|"]
    for system, shares in res["strategy_share"].items():
        lines.append(f"| {system} | " + " | ".join(
            f"{shares[st]['mean']:.3f} ± {shares[st]['sd']:.3f}" for st in STRATEGIES) + " |")
    lines += ["", "## Unilateral deviation from all-honest (mean payoff over seeds)", "",
              "| System | Agent | honest | strategic | manipulative | best | honest best in seeds |",
              "|---|---|---|---|---|---|---|"]
    for system, agents in res["unilateral_deviation"].items():
        for agent, row in agents.items():
            lines.append(f"| {system} | {agent} | {row['honest']:.3f} | {row['strategic']:.3f} | "
                         f"{row['manipulative']:.3f} | {row['best_response']} | "
                         f"{row['honest_is_best_in_n_seeds']}/{res['n_seeds']} |")
    lines += ["", f"Checkpoint verdicts (proposed vs baseline): {res['checkpoint']['verdicts']}; "
              f"continue = {res['checkpoint']['continue']}", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default="energy")
    args = parser.parse_args()
    result = analyse(args.domain)
    (ROOT / "results" / "summaries" / f"{args.domain}_main.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    (ROOT / "tables" / f"{args.domain}_main.md").write_text(to_markdown(result), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(to_markdown(result))
