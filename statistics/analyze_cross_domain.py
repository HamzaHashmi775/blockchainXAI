"""Cross-domain comparison and H6 (CLAUDE.md step 32; protocol 11.5 and A4.3).

    python statistics/analyze_cross_domain.py

No new tests are run: the relative improvements, Holm p-values and verdicts are read from
the saved per-domain summaries (results/summaries/{domain}_main.json for the classical
agents, {domain}_llm.json for the LLM agents). H6 holds for an outcome when both domains
give the same verdict (improved / negligible / worse) under the section 9 decision rule.
Writes results/summaries/cross_domain.json and tables/cross_domain.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = ("pharma", "energy")
H6_OUTCOMES = ("fidelity", "evidence_support", "manipulation")
# reported next to H6, not part of it (no verdict exists for them)
SECONDARY = ("collective_accuracy", "manipulation_success")
ARMS = {"classical": "{domain}_main.json", "llm": "{domain}_llm.json"}
COMPARISONS = ("proposed_vs_baseline", "ablation_vs_baseline")


def load(arm, domain, summaries):
    data = json.loads((summaries / ARMS[arm].format(domain=domain)).read_text())
    return data["main"] if arm == "llm" else data


def entry(cmp):
    out = {k: cmp.get(k) for k in ("mean_control", "mean_treatment", "mean_difference",
                                   "ci_low", "ci_high", "relative_improvement", "p_value",
                                   "p_holm", "test", "verdict")}
    return out


def analyse(summaries=ROOT / "results" / "summaries"):
    res = {"arms": {}}
    for arm in ARMS:
        data = {d: load(arm, d, summaries) for d in DOMAINS}
        arm_out = {"n_seeds": {d: data[d]["n_seeds"] for d in DOMAINS}, "comparisons": {}}
        for comparison in COMPARISONS:
            rows = {}
            for outcome in H6_OUTCOMES + SECONDARY:
                rows[outcome] = {d: entry(data[d]["comparisons"][comparison][outcome])
                                 for d in DOMAINS}
            h6 = {}
            for outcome in H6_OUTCOMES:
                verdicts = [rows[outcome][d]["verdict"] for d in DOMAINS]
                if None in verdicts:
                    raise ValueError(f"{arm} {comparison} {outcome}: verdict missing")
                h6[outcome] = {"verdicts": dict(zip(DOMAINS, verdicts)),
                               "same_verdict": verdicts[0] == verdicts[1]}
            arm_out["comparisons"][comparison] = {
                "outcomes": rows, "h6": h6,
                "h6_holds_for": [o for o in H6_OUTCOMES if h6[o]["same_verdict"]]}
        res["arms"][arm] = arm_out
    return res


def _pct(x):
    return "—" if x is None else f"{100 * x:+.1f}%"


def to_markdown(res):
    lines = ["# Cross-domain comparison (H6)", "",
             "Relative improvement = (treatment − baseline)/|baseline|, per domain, from the "
             "saved summaries; for manipulation a negative value is the improvement. Verdicts "
             "use the section 9 decision rule within each domain (Holm over F, E, M; "
             "|rel| ≥ 5 %). Domains are not pooled. H6 holds for an outcome when both "
             "domains give the same verdict.", ""]
    for arm, arm_out in res["arms"].items():
        n = arm_out["n_seeds"]
        for comparison, c in arm_out["comparisons"].items():
            lines += [f"## {arm} agents — {comparison.replace('_', ' ')} "
                      f"(n = {n['pharma']} pharma / {n['energy']} energy seeds)", "",
                      "| Outcome | Pharma rel. | Pharma Δ [95% CI] | Pharma verdict | "
                      "Energy rel. | Energy Δ [95% CI] | Energy verdict | Same verdict |",
                      "|---|---|---|---|---|---|---|---|"]
            for outcome, row in c["outcomes"].items():
                cells = []
                for d in DOMAINS:
                    r = row[d]
                    cells += [_pct(r["relative_improvement"]),
                              f"{r['mean_difference']:+.3f} [{r['ci_low']:+.3f}, "
                              f"{r['ci_high']:+.3f}]",
                              r["verdict"] or "— (secondary)"]
                same = ("yes" if c["h6"][outcome]["same_verdict"] else "no") \
                    if outcome in c["h6"] else "—"
                lines.append(f"| {outcome} | " + " | ".join(cells) + f" | {same} |")
            held = c["h6_holds_for"]
            lines += ["", f"H6 holds for: {', '.join(held) if held else 'none'} "
                          f"({len(held)} of {len(H6_OUTCOMES)}).", ""]
    return "\n".join(lines)


def main():
    res = analyse()
    out = ROOT / "results" / "summaries" / "cross_domain.json"
    out.write_text(json.dumps(res, indent=2, sort_keys=True))
    md = to_markdown(res)
    (ROOT / "tables" / "cross_domain.md").write_text(md + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
