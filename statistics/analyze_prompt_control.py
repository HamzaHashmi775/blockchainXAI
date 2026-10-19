"""Prompt-only control (protocol amendment 6): wording versus payoff.

    python statistics/analyze_prompt_control.py

Reads results/raw/pharma_llm_prompt_control/ and writes
results/summaries/pharma_llm_prompt_control.json and tables/pharma_llm_prompt_control.md.
Conditions: A = baseline wording and payoff, B = proposed wording with the baseline payoff,
C = proposed wording and payoff; the audit checks are shown in all three. This is an added,
post hoc experiment: the original LLM results were known when it was designed.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

sys.path.insert(0, str(ROOT / "statistics"))

from analyze_llm import SECONDARY, _get, load  # noqa: E402
from evaluation.stats import checkpoint_verdict, describe, holm, paired_comparison  # noqa: E402

RUN = "pharma_llm_prompt_control"
CONDITIONS = {"A": "baseline_shown", "B": "prompt_only", "C": "proposed"}
# contrast name -> (treatment, control, what it estimates)
CONTRASTS = {"B_vs_A": ("B", "A", "wording"),
             "C_vs_B": ("C", "B", "payoff, given the proposed wording"),
             "C_vs_A": ("C", "A", "wording and payoff together")}
PRIMARY = "mean_confidence"            # hypothesised direction: lower
VERDICT = {"improved": "lower", "worse": "higher", "negligible": "no detectable effect"}
OUTCOMES = {"mean_confidence": ("behaviour", "mean_confidence"),
            "confidence_inflation": ("behaviour", "confidence_inflation"),
            "votes_against_tool": ("behaviour", "votes_against_tool"),
            "manipulation": ("manipulation",), "fidelity": ("fidelity",),
            "evidence_support": ("evidence_support",),
            "collective_accuracy": ("collective_accuracy",),
            "component_strategic_voting": SECONDARY["component_strategic_voting"]}


def analyse(runs, original=None):
    seeds = sorted(runs)

    def series(cond, metric, source=None):
        source = source or runs
        name = CONDITIONS[cond] if source is runs else cond
        return np.array([_get(source[s]["systems"][name]["metrics"], OUTCOMES[metric])
                         for s in seeds], dtype=float)

    out = {"run": RUN, "seeds": seeds, "n_seeds": len(seeds),
           "model": runs[seeds[0]]["model"], "omega": runs[seeds[0]].get("omega"),
           "prompt_style": runs[seeds[0]].get("prompt_style"),
           "descriptive": {m: {c: describe(series(c, m)) for c in CONDITIONS}
                           for m in OUTCOMES},
           "contrasts": {}}
    calls = [runs[s]["systems"][n]["metrics"]["calls"] for s in seeds
             for n in CONDITIONS.values()]
    out["calls"] = {k: int(sum(c[k] for c in calls))
                    for k in ("total", "unusable_replies", "reports_replaced_by_tool_report")}
    for name, (t, c, meaning) in CONTRASTS.items():
        out["contrasts"][name] = {"estimates": meaning, **{
            m: paired_comparison(series(t, m), series(c, m)) for m in OUTCOMES}}
    # confirmatory family of this amendment: the primary outcome over the three contrasts
    adjusted = holm([out["contrasts"][n][PRIMARY]["p_value"] for n in CONTRASTS])
    for n, p_adj in zip(CONTRASTS, adjusted):
        comp = out["contrasts"][n][PRIMARY]
        comp["p_holm"] = float(p_adj)
        # decision rule of the protocol (Holm p < 0.05 and |relative change| >= 5 %)
        comp["verdict"] = VERDICT[checkpoint_verdict(comp, p_adj, False)]
    lowered = {n: out["contrasts"][n][PRIMARY]["verdict"] == "lower" for n in CONTRASTS}
    if lowered["B_vs_A"] and lowered["C_vs_B"]:
        reading = "both: wording and payoff each lower confidence"
    elif lowered["B_vs_A"]:
        reading = "wording: the stated rules lower confidence; the payoff adds no detectable effect"
    elif lowered["C_vs_B"]:
        reading = "payoff: the payoff lowers confidence; the wording alone does not detectably"
    else:
        reading = "neither contrast meets the decision rule on its own"
    out["reading"] = reading
    combined = series("C", PRIMARY) - series("A", PRIMARY)
    wording = series("B", PRIMARY) - series("A", PRIMARY)
    # ratio of mean effects (a per-seed ratio is unstable when C - A is near zero)
    out["share_of_combined_effect_from_wording"] = (
        float(wording.mean() / combined.mean()) if combined.mean() != 0 else None)
    if original is not None:
        # descriptive checks against the main run (same seeds and rounds)
        out["checks_against_main_run"] = {
            "C_vs_original_proposed": {m: paired_comparison(series("C", m), series(
                "proposed", m, original)) for m in ("mean_confidence", "fidelity")},
            "A_vs_original_baseline": {m: paired_comparison(series("A", m), series(
                "baseline", m, original)) for m in ("mean_confidence", "fidelity")}}
    return out


def _cell(d):
    return f"{d['mean']:.3f} ± {d['sd']:.3f}"


def to_markdown(res):
    lines = [
        "# Prompt-only control (pharma, LLM agents) — added, post hoc experiment",
        "",
        f"Model `{res['model'].get('model')}`; n = {res['n_seeds']} paired seeds; ω = "
        f"{res['omega']}; prompt style `{res['prompt_style']}`. A = baseline wording and "
        "payoff; B = proposed wording, baseline payoff; C = proposed wording and payoff. "
        "Audit checks shown in the round history in all three. Designed after the main "
        "results were known (amendment 6).",
        f"Model calls: {res['calls']['total']}; unusable replies: "
        f"{res['calls']['unusable_replies']}; reports replaced by the tool's report: "
        f"{res['calls']['reports_replaced_by_tool_report']}.",
        "",
        "| Outcome | A | B | C |",
        "|---|---|---|---|",
    ]
    for m, by in res["descriptive"].items():
        lines.append(f"| {m} | {_cell(by['A'])} | {_cell(by['B'])} | {_cell(by['C'])} |")
    for name, comp in res["contrasts"].items():
        lines += ["", f"## {name.replace('_vs_', ' vs ')} — {comp['estimates']}", "",
                  "| Outcome | Δ mean | 95% CI | Rel. | Test | p | p (Holm) | Verdict |",
                  "|---|---|---|---|---|---|---|---|"]
        for m in OUTCOMES:
            c = comp[m]
            primary = m == PRIMARY
            lines.append(
                f"| {m}{'' if primary else ' (secondary)'} | {c['mean_difference']:+.3f} | "
                f"[{c['ci_low']:+.3f}, {c['ci_high']:+.3f}] | "
                f"{100 * c['relative_improvement']:+.1f}% | {c['test']} | {c['p_value']:.4f} | "
                + (f"{c['p_holm']:.4f} | {c['verdict']} |" if primary else "— | — |"))
    share = res["share_of_combined_effect_from_wording"]
    lines += ["", f"Reading (pre-declared rule): **{res['reading']}**.",
              f"Share of the combined effect on {PRIMARY} that B already shows "
              f"(mean(B − A) / mean(C − A)): "
              + ("undefined" if share is None else f"{share:.2f}") + " (descriptive)."]
    if "checks_against_main_run" in res:
        lines += ["", "Descriptive checks against the main run (same seeds and rounds):"]
        for name, by in res["checks_against_main_run"].items():
            parts = [f"{m} Δ {c['mean_difference']:+.3f} (p {c['p_value']:.3f})"
                     for m, c in by.items()]
            lines.append(f"- {name}: " + "; ".join(parts))
    return "\n".join(lines) + "\n"


def main():
    runs = load(RUN)
    if not runs:
        raise SystemExit(f"no results in results/raw/{RUN}")
    original = load("pharma_llm_main") or None
    res = analyse(runs, original)
    (ROOT / "results" / "summaries" / f"{RUN}.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8")
    text = to_markdown(res)
    (ROOT / "tables" / f"{RUN}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
