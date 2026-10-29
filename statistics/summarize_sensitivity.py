"""Robustness of the main conclusions across the sensitivity runs (CLAUDE.md step 33).

    python statistics/summarize_sensitivity.py

Reads results/summaries/{domain}_sensitivity_{parameter}.json (written by
analyze_sensitivity.py) and {domain}_main.json. For each pre-declared value it compares the
section 9 verdict of proposed vs baseline on F, E and M with the verdict of the main run.
Exploratory values are listed but do not count towards "robust". Writes
results/summaries/sensitivity_robustness.json and tables/sensitivity_robustness.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = ("pharma", "energy")
PARAMETERS = ("beta", "rho", "omega")
OUTCOMES = ("fidelity", "evidence_support", "manipulation")


def analyse(summaries=ROOT / "results" / "summaries"):
    res = {"runs": {}, "missing": []}
    for domain in DOMAINS:
        main = json.loads((summaries / f"{domain}_main.json").read_text())
        reference = {o: main["comparisons"]["proposed_vs_baseline"][o]["verdict"]
                     for o in OUTCOMES}
        for parameter in PARAMETERS:
            name = f"{domain}_sensitivity_{parameter}"
            path = summaries / f"{name}.json"
            if not path.exists():
                res["missing"].append(name)
                continue
            sens = json.loads(path.read_text())
            exploratory = set(sens["exploratory_values"])
            rows = {}
            for value, entry in sens["by_value"].items():
                verdicts = {o: entry["proposed_vs_baseline"][o]["verdict"] for o in OUTCOMES}
                rows[value] = {
                    "exploratory": value in exploratory,
                    "verdicts": verdicts,
                    "relative_improvement": {
                        o: entry["proposed_vs_baseline"][o]["relative_improvement"]
                        for o in OUTCOMES},
                    "same_as_main": {o: verdicts[o] == reference[o] for o in OUTCOMES}}
            declared = [r for r in rows.values() if not r["exploratory"]]
            res["runs"][name] = {
                "domain": domain, "parameter": sens["parameter"], "main_verdicts": reference,
                "values": rows,
                "robust": {o: all(r["same_as_main"][o] for r in declared) for o in OUTCOMES}}
    return res


def to_markdown(res):
    lines = ["# Sensitivity: are the main verdicts robust?", "",
             "Proposed vs baseline, section 9 verdict per value (Holm over F, E, M within each "
             "value; |rel| ≥ 5 % for 'improved'). 'Robust' = the verdict at every pre-declared "
             "value equals the main run's; exploratory values (marked *) are shown but not "
             "counted. One parameter varied at a time, 10 seeds per value.", ""]
    if res["missing"]:
        lines += [f"Not yet run: {', '.join(res['missing'])}.", ""]
    for name, run in res["runs"].items():
        lines += [f"## {name} (`{run['parameter']}`)", "",
                  "| Value | " + " | ".join(OUTCOMES) + " |",
                  "|---|" + "---|" * len(OUTCOMES),
                  "| main run | " + " | ".join(run["main_verdicts"][o] for o in OUTCOMES) + " |"]
        for value, row in run["values"].items():
            label = value + ("*" if row["exploratory"] else "")
            lines.append(f"| {label} | " + " | ".join(
                f"{row['verdicts'][o]} ({row['relative_improvement'][o]:+.1%})"
                for o in OUTCOMES) + " |")
        lines += ["", "Robust: " + ", ".join(
            f"{o} {'yes' if run['robust'][o] else 'no'}" for o in OUTCOMES), ""]
    return "\n".join(lines)


def main():
    res = analyse()
    (ROOT / "results" / "summaries" / "sensitivity_robustness.json").write_text(
        json.dumps(res, indent=2, sort_keys=True))
    md = to_markdown(res)
    (ROOT / "tables" / "sensitivity_robustness.md").write_text(md + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
