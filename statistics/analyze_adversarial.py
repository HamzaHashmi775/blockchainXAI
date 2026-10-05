"""Robustness analysis: malicious-agent share and collusion (protocol sections 8-9).

    python statistics/analyze_adversarial.py --domain energy

Reads results/raw/<domain>_adversarial/seed_*.json; writes
results/summaries/<domain>_adversarial.json and tables/<domain>_adversarial.md.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.stats import describe, friedman, holm, paired_comparison  # noqa: E402

METRICS = ("collective_accuracy", "fidelity", "evidence_support", "manipulation",
           "manipulation_success", "collective_utility", "fidelity_non_malicious",
           "manipulation_non_malicious")
COLLUSION_METRICS = ("collective_accuracy", "collective_utility", "manipulation_success")


def analyse(domain):
    folder = ROOT / "results" / "raw" / f"{domain}_adversarial"
    manifest = json.loads((folder / "manifest.json").read_text())
    if manifest["status"] != "completed":
        raise SystemExit(f"{folder} has no completed run")
    seeds = manifest["seeds"]
    runs = {seed: json.loads((folder / f"seed_{seed}.json").read_text()) for seed in seeds}
    systems = list(runs[seeds[0]]["systems"])
    fractions = list(runs[seeds[0]]["systems"][systems[0]]["malicious"])

    def series(system, fraction, metric):
        return np.array([runs[s]["systems"][system]["malicious"][fraction][metric] for s in seeds])

    out = {"domain": domain, "seeds": seeds, "fractions": fractions, "systems": systems,
           "descriptive": {m: {sy: {f: describe(series(sy, f, m)) for f in fractions}
                               for sy in systems} for m in METRICS}}

    # decision degradation under attack: accuracy(p=0) - accuracy(p)
    attacked = [f for f in fractions if float(f) > 0]
    degradation = {sy: {f: series(sy, fractions[0], "collective_accuracy")
                        - series(sy, f, "collective_accuracy") for f in attacked} for sy in systems}
    out["degradation"] = {sy: {f: describe(v) for f, v in d.items()} for sy, d in degradation.items()}
    out["friedman_accuracy_across_fractions"] = {
        sy: friedman([series(sy, f, "collective_accuracy") for f in fractions]) for sy in systems}
    if {"proposed", "baseline"} <= set(systems):
        mean_deg = {sy: np.mean([degradation[sy][f] for f in attacked], axis=0) for sy in systems}
        out["h4_primary_mean_degradation"] = paired_comparison(mean_deg["proposed"],
                                                               mean_deg["baseline"])
        per_fraction = {f: paired_comparison(degradation["proposed"][f], degradation["baseline"][f])
                        for f in attacked}
        for f, p in zip(attacked, holm([per_fraction[f]["p_value"] for f in attacked])):
            per_fraction[f]["p_holm"] = float(p)
        out["h4_per_fraction"] = per_fraction
        out["accuracy_proposed_vs_baseline"] = {
            f: paired_comparison(series("proposed", f, "collective_accuracy"),
                                 series("baseline", f, "collective_accuracy")) for f in fractions}

    # collusion: two colluders, three honest agents, vs the same runs without collusion
    collusion = {}
    for sy in systems:
        def col(condition, metric):
            return np.array([runs[s]["systems"][sy]["collusion"][condition][metric] for s in seeds])

        def colluder_mean(condition, field):
            return np.array([np.mean([runs[s]["systems"][sy]["collusion"][condition]["per_agent"]
                                      [a][field] for a in runs[s]["colluders"]]) for s in seeds])

        def honest_mean(condition, field):
            return np.array([np.mean([v[field] for a, v in runs[s]["systems"][sy]["collusion"]
                                      [condition]["per_agent"].items()
                                      if a not in runs[s]["colluders"]]) for s in seeds])

        entry = {m: paired_comparison(col("with", m), col("without", m)) for m in COLLUSION_METRICS}
        for field in ("private_utility", "reward", "payoff"):
            entry[f"colluders_{field}"] = paired_comparison(colluder_mean("with", field),
                                                            colluder_mean("without", field))
            entry[f"honest_agents_{field}"] = paired_comparison(honest_mean("with", field),
                                                                honest_mean("without", field))
        if runs[seeds[0]]["systems"][sy]["collusion"]["with"]["per_agent"][
                runs[seeds[0]]["colluders"][0]]["final_reputation"] is not None:
            entry["colluders_final_reputation"] = paired_comparison(
                colluder_mean("with", "final_reputation"),
                colluder_mean("without", "final_reputation"))
        collusion[sy] = entry
    out["collusion"] = collusion
    return out


def to_markdown(res):
    lines = [f"# {res['domain'].capitalize()} — robustness to malicious agents", "",
             f"n = {len(res['seeds'])} seeds; mean ± SD. Malicious agents always play "
             "*manipulative*; 10% and 30% are realised in expectation over rounds.", ""]
    for metric, by_system in res["descriptive"].items():
        lines += [f"## {metric}", "", "| System | " + " | ".join(
            f"{float(f):.0%}" for f in res["fractions"]) + " |",
            "|---|" + "---|" * len(res["fractions"])]
        for system, by_fraction in by_system.items():
            lines.append(f"| {system} | " + " | ".join(
                f"{by_fraction[f]['mean']:.3f} ± {by_fraction[f]['sd']:.3f}"
                for f in res["fractions"]) + " |")
        lines.append("")
    lines += ["## Accuracy degradation: accuracy(0%) − accuracy(p)", ""]
    for system, by_fraction in res["degradation"].items():
        lines.append(f"- {system}: " + ", ".join(
            f"{float(f):.0%}: {d['mean']:+.3f} ± {d['sd']:.3f}" for f, d in by_fraction.items()))
    for system, fr in res["friedman_accuracy_across_fractions"].items():
        lines.append(f"- Friedman across shares, {system}: χ² = {fr['statistic']:.2f}, "
                     f"p = {fr['p_value']:.4g}")
    if "h4_primary_mean_degradation" in res:
        c = res["h4_primary_mean_degradation"]
        lines += ["", "## H4 primary: mean degradation over 10–40%, proposed − baseline", "",
                  f"Δ = {c['mean_difference']:+.4f} (95% CI [{c['ci_low']:+.4f}, {c['ci_high']:+.4f}]), "
                  f"{c['test']}, p = {c['p_value']:.4g}, {c['effect_size_name']} = "
                  f"{c['effect_size']:.2f}. Negative Δ = proposed degrades less.", "",
                  "| Share | Δ degradation | p | p (Holm) |", "|---|---|---|---|"]
        for f, c in res["h4_per_fraction"].items():
            lines.append(f"| {float(f):.0%} | {c['mean_difference']:+.4f} | {c['p_value']:.4g} "
                         f"| {c['p_holm']:.4g} |")
        lines += ["", "## Collective accuracy, proposed − baseline at each share", "",
                  "| Share | Δ accuracy | 95% CI | test | p (unadjusted) |", "|---|---|---|---|---|"]
        for f, c in res["accuracy_proposed_vs_baseline"].items():
            lines.append(f"| {float(f):.0%} | {c['mean_difference']:+.4f} | "
                         f"[{c['ci_low']:+.4f}, {c['ci_high']:+.4f}] | {c['test']} | "
                         f"{c['p_value']:.4g} |")
    lines += ["", "## Collusion (2 colluders + 3 honest) vs no collusion", "",
              "| System | Quantity | Without | With | Δ | p (unadjusted) |", "|---|---|---|---|---|---|"]
    for system, entry in res["collusion"].items():
        for name, c in entry.items():
            lines.append(f"| {system} | {name} | {c['mean_control']:.3f} | {c['mean_treatment']:.3f} "
                         f"| {c['mean_difference']:+.3f} | {c['p_value']:.4g} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default="energy")
    args = parser.parse_args()
    result = analyse(args.domain)
    (ROOT / "results" / "summaries" / f"{args.domain}_adversarial.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    (ROOT / "tables" / f"{args.domain}_adversarial.md").write_text(to_markdown(result),
                                                                  encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(to_markdown(result))
