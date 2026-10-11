"""LLM-agent experiments (protocol amendment 3): statistics for one case study.

    python statistics/analyze_llm.py --domain pharma

Reads results/raw/<domain>_llm_main/ (and <domain>_llm_adversarial/ if present); writes
results/summaries/<domain>_llm.json and tables/<domain>_llm.md. Every number comes from
the saved runs.
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
CONFIRMATORY = {"fidelity": True, "evidence_support": True, "manipulation": False}
# pre-declared secondary outcomes: name -> path inside a system's metrics
SECONDARY = {
    "votes_against_tool": ("behaviour", "votes_against_tool"),
    "confidence_inflation": ("behaviour", "confidence_inflation"),
    "votes_own_preferred_option": ("behaviour", "votes_own_preferred_option"),
    "fully_truthful_explanation": ("behaviour", "fully_truthful_explanation"),
    "collective_accuracy": ("collective_accuracy",),
    "manipulation_success": ("manipulation_success",),
}
MIN_WILCOXON_P = {5: 0.0625, 3: 0.25}


def load(name):
    folder = ROOT / "results" / "raw" / name
    files = sorted(folder.glob("seed_*.json"), key=lambda p: int(p.stem.split("_")[1]))
    return {int(p.stem.split("_")[1]): json.loads(p.read_text()) for p in files}


def _get(metrics, path):
    for key in path:
        metrics = metrics[key]
    return metrics


def _accuracy(rounds, n):
    return float(np.mean(np.array(rounds["collective"][:n]) == np.array(rounds["reference"][:n])))


def analyse_main(runs):
    seeds = sorted(runs)
    paths = {**{m: (m,) for m in CONFIRMATORY}, **SECONDARY}

    def series(system, metric):
        return np.array([_get(runs[s]["systems"][system]["metrics"], paths[metric])
                         for s in seeds], dtype=float)

    out = {"seeds": seeds, "n_seeds": len(seeds),
           "model": runs[seeds[0]]["model"], "environment": runs[seeds[0]]["environment"],
           "descriptive": {m: {s: describe(series(s, m)) for s in SYSTEMS} for m in paths},
           "comparisons": {}}
    calls = [runs[s]["systems"][name]["metrics"]["calls"] for s in seeds for name in SYSTEMS]
    out["calls"] = {"total": int(sum(c["total"] for c in calls)),
                    "unusable_replies": int(sum(c["unusable_replies"] for c in calls)),
                    "reports_replaced_by_tool_report": int(
                        sum(c["reports_replaced_by_tool_report"] for c in calls))}
    for treatment in ("proposed", "ablation"):
        comp = {m: paired_comparison(series(treatment, m), series("baseline", m)) for m in paths}
        adjusted = holm([comp[m]["p_value"] for m in CONFIRMATORY])
        for m, p_adj in zip(CONFIRMATORY, adjusted):
            comp[m]["p_holm"] = float(p_adj)
            comp[m]["verdict"] = checkpoint_verdict(comp[m], p_adj, CONFIRMATORY[m])
        out["comparisons"][f"{treatment}_vs_baseline"] = comp
    verdicts = {m: out["comparisons"]["proposed_vs_baseline"][m]["verdict"] for m in CONFIRMATORY}
    out["verdicts"] = verdicts
    return out


def analyse_adversarial(main, adversarial):
    seeds = sorted(adversarial)
    rounds = adversarial[seeds[0]]["rounds_played"]
    systems = list(adversarial[seeds[0]]["systems"])
    shares = list(adversarial[seeds[0]]["systems"][systems[0]]["malicious"])
    accuracy = {s: {"0.0": [_accuracy(main[k]["systems"][s]["rounds"], rounds) for k in seeds],
                    **{p: [adversarial[k]["systems"][s]["malicious"][p]["metrics"]
                           ["collective_accuracy"] for k in seeds] for p in shares}}
                for s in systems}
    degradation = {s: {p: (np.array(accuracy[s]["0.0"]) - np.array(accuracy[s][p])).tolist()
                       for p in shares} for s in systems}
    mean_deg = {s: np.mean([degradation[s][p] for p in shares], axis=0) for s in systems}
    out = {"seeds": seeds, "n_seeds": len(seeds), "rounds": rounds, "shares": shares,
           "accuracy": {s: {p: describe(v) for p, v in accuracy[s].items()} for s in systems},
           "degradation": {s: {p: describe(v) for p, v in degradation[s].items()}
                           for s in systems},
           "h4_mean_degradation_proposed_minus_baseline": paired_comparison(
               mean_deg["proposed"], mean_deg["baseline"]),
           "llm_agents_under_attack": {
               s: {p: {m: describe([adversarial[k]["systems"][s]["malicious"][p]["metrics"]
                                    ["llm_agents"][m] for k in seeds])
                       for m in ("fidelity", "evidence_support", "manipulation")}
                   for p in shares} for s in systems},
           "collusion": {}}
    for s in systems:
        with_c = [adversarial[k]["systems"][s]["collusion"]["metrics"] for k in seeds]
        out["collusion"][s] = {
            "accuracy_without": describe(accuracy[s]["0.0"]),
            "accuracy_with": describe([m["collective_accuracy"] for m in with_c]),
            "manipulation_success_with": describe([m["manipulation_success"] for m in with_c]),
            "colluders_reward": describe([m["scripted_agents"]["reward"] for m in with_c]),
            "colluders_payoff": describe([m["scripted_agents"]["payoff"] for m in with_c]),
            "colluders_private_utility": describe(
                [m["scripted_agents"]["private_utility"] for m in with_c]),
            "llm_agents_reward": describe([m["llm_agents"]["reward"] for m in with_c]),
            "llm_agents_payoff": describe([m["llm_agents"]["payoff"] for m in with_c])}
        reputations = [m["scripted_agents"]["final_reputation"] for m in with_c]
        if all(r is not None for r in reputations):
            out["collusion"][s]["colluders_final_reputation"] = describe(reputations)
    return out


def _cell(d):
    return f"{d['mean']:.3f} ± {d['sd']:.3f}"


def to_markdown(domain, res):
    main = res["main"]
    n = main["n_seeds"]
    model = main["model"]
    lines = [f"# {domain.capitalize()} — LLM agents: baseline vs ablation vs proposed", "",
             f"Model `{model.get('model')}` (digest `{str(model.get('digest'))[:12]}`); "
             f"n = {n} paired seeds; mean ± SD over seeds; all rounds, all agents.",
             f"Model calls: {main['calls']['total']}; unusable replies: "
             f"{main['calls']['unusable_replies']}; reports replaced by the tool's report: "
             f"{main['calls']['reports_replaced_by_tool_report']}.",
             f"With n = {n} a Wilcoxon test cannot give p < {MIN_WILCOXON_P.get(n, 'n/a')}; "
             "rows tested that way are not significant by construction.", "",
             "| Metric | Baseline | Ablation | Proposed |", "|---|---|---|---|"]
    for metric, by_system in main["descriptive"].items():
        lines.append(f"| {metric} | " + " | ".join(_cell(by_system[s]) for s in SYSTEMS) + " |")
    for name, comp in main["comparisons"].items():
        lines += ["", f"## {name.replace('_', ' ')}", "",
                  "| Metric | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Effect | Verdict |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for metric, c in comp.items():
            family = "" if metric in CONFIRMATORY else " (secondary)"
            lines.append(
                f"| {metric}{family} | {c['mean_difference']:+.3f} | [{c['ci_low']:+.3f}, "
                f"{c['ci_high']:+.3f}] | {c['relative_improvement']:+.1%} | {c['test']} "
                f"| {c['p_value']:.4f} | {c.get('p_holm', float('nan')):.4f} "
                f"| {c['effect_size_name']} = {c['effect_size']:.2f} | {c.get('verdict', '—')} |")
    lines += ["", f"Verdicts (proposed vs baseline): {main['verdicts']}", ""]
    adv = res.get("adversarial")
    if adv:
        lines += [f"## Robustness (n = {adv['n_seeds']} seeds, first {adv['rounds']} rounds; "
                  "descriptive only)", "",
                  "Scripted malicious agents among LLM agents. Share 0 = same rounds of the "
                  "main run.", "",
                  "| System | " + " | ".join(f"acc. at {p}" for p in ["0.0", *adv["shares"]])
                  + " |", "|---|" + "---|" * (len(adv["shares"]) + 1)]
        for s, by_share in adv["accuracy"].items():
            lines.append(f"| {s} | " + " | ".join(
                _cell(by_share[p]) for p in ["0.0", *adv["shares"]]) + " |")
        h4 = adv["h4_mean_degradation_proposed_minus_baseline"]
        lines += ["", f"H4: mean degradation, proposed − baseline = {h4['mean_difference']:+.3f} "
                  f"(95% CI [{h4['ci_low']:+.3f}, {h4['ci_high']:+.3f}], {h4['test']}, "
                  f"p = {h4['p_value']:.4f}). Negative = proposed degrades less. Three seeds: "
                  "no confirmatory claim.", "",
                  "### LLM agents' own reports under attack", "",
                  "| System | Share | Fidelity | Evidence | Manipulation |", "|---|---|---|---|---|"]
        for s, by_share in adv["llm_agents_under_attack"].items():
            for p, m in by_share.items():
                lines.append(f"| {s} | {p} | {_cell(m['fidelity'])} | "
                             f"{_cell(m['evidence_support'])} | {_cell(m['manipulation'])} |")
        lines += ["", "### Collusion (2 scripted colluders + 3 LLM agents)", "",
                  "| System | Quantity | Value |", "|---|---|---|"]
        for s, rows in adv["collusion"].items():
            for name, d in rows.items():
                lines.append(f"| {s} | {name} | {_cell(d)} |")
        lines.append("")
    return "\n".join(lines)


def analyse(domain):
    main = load(f"{domain}_llm_main")
    if not main:
        raise SystemExit(f"no results in results/raw/{domain}_llm_main")
    res = {"domain": domain, "main": analyse_main(main)}
    adversarial = load(f"{domain}_llm_adversarial")
    if adversarial:
        missing = sorted(set(adversarial) - set(main))
        if missing:
            raise SystemExit(f"adversarial seeds {missing} have no main run to compare with")
        res["adversarial"] = analyse_adversarial(main, adversarial)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default="pharma")
    args = parser.parse_args()
    result = analyse(args.domain)
    (ROOT / "results" / "summaries" / f"{args.domain}_llm.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    text = to_markdown(args.domain, result)
    (ROOT / "tables" / f"{args.domain}_llm.md").write_text(text, encoding="utf-8")
    print(text)
