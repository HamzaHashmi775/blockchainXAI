"""Final statistics: every hypothesis with its verdict, in one place (CLAUDE.md step 34).

    python statistics/final_summary.py

Runs no new tests. Every number is read from results/summaries/ (written by the other
analysis scripts):
- H1-H3: section 9 verdicts of proposed vs baseline ({domain}_main.json, {domain}_llm.json).
- H4: the pre-declared primary comparison (section 7: mean accuracy degradation over shares
  0.1-0.4, proposed - baseline, paired, two-sided, alpha 0.05). Verdict "supported" if
  p < 0.05 and the proposed system degrades less (difference < 0); "opposite" if p < 0.05
  the other way; otherwise "not supported". LLM agents: 3 seeds, no confirmatory claim (A4.3).
- H5: detection and false-positive rates (provenance.json; descriptive, section 7).
- H6: cross_domain.json. Sensitivity: sensitivity_robustness.json.
Writes results/summaries/final_statistics.json and tables/final_statistics.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = ("pharma", "energy")
H13 = {"H1": "fidelity", "H2": "evidence_support", "H3": "manipulation"}
ALPHA = 0.05


def h4_verdict(cmp):
    p, diff = cmp["p_value"], cmp["mean_difference"]
    if p < ALPHA:
        return "supported" if diff < 0 else "opposite"
    return "not supported"


def _cmp(c, keys=("mean_difference", "ci_low", "ci_high", "p_value", "test", "n")):
    return {k: c.get(k) for k in keys}


def analyse(summaries=ROOT / "results" / "summaries"):
    def load(name):
        return json.loads((summaries / f"{name}.json").read_text())

    res = {"H1_H3": {}, "H4": {}, "H5": {}, "H6": {}, "sensitivity": {}}
    for arm in ("classical", "llm"):
        res["H1_H3"][arm] = {}
        for d in DOMAINS:
            data = load(f"{d}_main") if arm == "classical" else load(f"{d}_llm")["main"]
            comps = data["comparisons"]["proposed_vs_baseline"]
            res["H1_H3"][arm][d] = {
                h: dict(_cmp(comps[m], ("mean_control", "mean_treatment", "mean_difference",
                                        "ci_low", "ci_high", "relative_improvement",
                                        "p_holm", "test")),
                        outcome=m, verdict=comps[m]["verdict"])
                for h, m in H13.items()}
            res["H1_H3"][arm][d]["n_seeds"] = data["n_seeds"]
    res["H4"]["classical"] = {}
    res["H4"]["llm"] = {}
    for d in DOMAINS:
        cmp = load(f"{d}_adversarial")["h4_primary_mean_degradation"]
        res["H4"]["classical"][d] = dict(_cmp(cmp), verdict=h4_verdict(cmp))
        llm = load(f"{d}_llm")["adversarial"]["h4_mean_degradation_proposed_minus_baseline"]
        res["H4"]["llm"][d] = dict(_cmp(llm), verdict="no confirmatory claim (3 seeds)")
    prov = load("provenance")
    res["H5"] = {"records": prov["records"], "detection_rate": prov["detection_rate"],
                 "detection_rate_all_targets": prov["detection_rate_all_targets"],
                 "false_positive_rate": prov["false_positive_rate"],
                 "below_resolution_detected": prov["below_resolution_detected"],
                 "verification": prov["verification"]}
    cross = load("cross_domain")
    res["H6"] = {arm: {"holds_for": cross["arms"][arm]["comparisons"]
                       ["proposed_vs_baseline"]["h6_holds_for"]} for arm in cross["arms"]}
    robust = load("sensitivity_robustness")
    res["sensitivity"] = {"missing": robust["missing"],
                          "robust": {n: r["robust"] for n, r in robust["runs"].items()}}
    return res


def _p(p):
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"


def _rel(x):
    return f"{100 * x:+.1f}%"


def to_markdown(res):
    lines = ["# Final statistics: all hypotheses", "",
             "Assembled from `results/summaries/`; no test is run here. Verdict rules are the "
             "pre-declared ones (protocol §7, §9, §11.5). Domains are never pooled.", "",
             "## H1–H3, proposed vs baseline", "",
             "| Agents | Domain | n | H1 fidelity | H2 evidence | H3 manipulation |",
             "|---|---|---|---|---|---|"]
    for arm, by_domain in res["H1_H3"].items():
        for d, row in by_domain.items():
            cells = [f"{row[h]['verdict']} ({_rel(row[h]['relative_improvement'])}, "
                     f"Holm p {_p(row[h]['p_holm'])})" for h in H13]
            lines.append(f"| {arm} | {d} | {row['n_seeds']} | " + " | ".join(cells) + " |")
    lines += ["", "## H4, robustness to 10–40 % malicious agents", "",
              "Primary: mean accuracy degradation over shares 0.1–0.4, proposed − baseline "
              "(negative = proposed degrades less).", "",
              "| Agents | Domain | n | Δ [95% CI] | test | p | Verdict |",
              "|---|---|---|---|---|---|---|"]
    for arm, by_domain in res["H4"].items():
        for d, c in by_domain.items():
            lines.append(f"| {arm} | {d} | {c['n']} | {c['mean_difference']:+.4f} "
                         f"[{c['ci_low']:+.4f}, {c['ci_high']:+.4f}] | {c['test']} | "
                         f"{_p(c['p_value'])} | {c['verdict']} |")
    h5 = res["H5"]
    controls = sum(h5["verification"][g]["VALID"] + h5["verification"][g]["TAMPERED"]
                   for g in h5["verification"] if g.startswith(("control", "all_untouched")))
    lines += ["", "## H5, tamper detection (descriptive)", "",
              f"Detection rate {h5['detection_rate_all_targets']:.3f} over all targets "
              f"({', '.join(f'{k} {v:.3f}' for k, v in h5['detection_rate'].items())}); "
              f"false-positive rate {h5['false_positive_rate']:.3f} over {controls:,} unchanged "
              f"records; changes below the 10⁻⁶ resolution detected: "
              f"{h5['below_resolution_detected']} (invisible by design). "
              f"{h5['records']:,} records on a local chain. Integrity, not truth.", "",
              "## H6, same verdict in both domains (proposed vs baseline)", ""]
    for arm, h6 in res["H6"].items():
        held = h6["holds_for"]
        lines.append(f"- {arm}: {len(held)} of 3 ({', '.join(held) if held else 'none'})")
    lines += ["", "## Sensitivity: are the H1–H3 verdicts unchanged at every pre-declared "
              "value?", "", "| Run | fidelity | evidence | manipulation |", "|---|---|---|---|"]
    for name, rob in res["sensitivity"]["robust"].items():
        lines.append(f"| {name} | " + " | ".join(
            "yes" if rob[o] else "**no**" for o in H13.values()) + " |")
    if res["sensitivity"]["missing"]:
        lines.append(f"\nNot run: {', '.join(res['sensitivity']['missing'])}.")
    lines += ["", "## Limits of inference", "",
              "- n = 10 seeds (classical) and 5 (LLM; 3 for LLM adversarial runs); the tests "
              "measure variation across seeds on one dataset per domain, not generalisation to "
              "other datasets.",
              "- Decision accuracy is agreement with a constructed reference decision.",
              "- H4 'not supported' means no difference was detected, not that there is none.",
              "- LLM 2×2 wording × payoff results (amendments 7–8) are post hoc and reported "
              "separately (`tables/*_llm_factorial.md`)."]
    return "\n".join(lines)


def main():
    res = analyse()
    (ROOT / "results" / "summaries" / "final_statistics.json").write_text(
        json.dumps(res, indent=2, sort_keys=True))
    md = to_markdown(res)
    (ROOT / "tables" / "final_statistics.md").write_text(md + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
