"""One command to rebuild the results (CLAUDE.md step 36).

    python reproduce.py                    # analyses -> results/summaries, tables, figures
    python reproduce.py --experiments      # first rerun every classical experiment (CPU)
    python reproduce.py --compare OTHER    # compare per-seed results with another checkout

The classical experiments (configs below) run on a CPU in about 1-2 hours in total. The LLM
experiments need Ollama with qwen2.5:7b and a GPU (see kaggle/); they are not rerun here.
Their raw results are git-ignored, so their analyses run only when results/raw/<run>/ exists;
otherwise the committed summaries are used as they are. The provenance experiment needs a
local anvil node (configs/provenance.yaml) and is not rerun here either.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "results" / "raw"

CLASSICAL = [f"{d}_{e}" for d in ("pharma", "energy")
             for e in ("baseline", "ablation", "proposed", "adversarial")]
SENSITIVITY = [f"{d}_sensitivity_{p}" for d in ("pharma", "energy")
               for p in ("beta", "rho", "omega")]

# (script and arguments, raw run folders it needs)
ANALYSES = [
    *[(["analyze_main.py", "--domain", d], [f"{d}_{s}" for s in ("baseline", "ablation",
                                                                   "proposed")])
      for d in ("pharma", "energy")],
    *[(["analyze_adversarial.py", "--domain", d], [f"{d}_adversarial"])
      for d in ("pharma", "energy")],
    *[(["analyze_sensitivity.py", "--name", n], [n]) for n in SENSITIVITY],
    *[(["analyze_llm.py", "--domain", d], [f"{d}_llm_main", f"{d}_llm_adversarial"])
      for d in ("pharma", "energy")],
    (["analyze_llm.py", "--domain", "pharma", "--run", "pharma_llm_main_w075"],
     ["pharma_llm_main_w075"]),
    (["analyze_prompt_control.py"], ["pharma_llm_prompt_control"]),
    *[(["analyze_factorial.py", "--domain", d],
       [f"{d}_llm_prompt_control", f"{d}_llm_prompt_control_d"]) for d in ("pharma", "energy")],
    (["summarize_sensitivity.py"], []),
    (["analyze_cross_domain.py"], []),
    (["final_summary.py"], []),
    (["make_tables.py"], []),
    (["make_figures.py"], []),
    (["../paper/make_paper_tables.py"], []),
]


def run(cmd):
    print("$", " ".join(cmd), flush=True)
    # UTF-8 output: the analyses print symbols (Δ, ω) that a Windows console code page lacks
    subprocess.run([sys.executable, *cmd], cwd=ROOT, check=True,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                   stdout=subprocess.DEVNULL if cmd[0].startswith("statistics") else None)


def experiments():
    for name in CLASSICAL + SENSITIVITY:
        run(["run_experiment.py", "--config", f"configs/{name}.yaml", "--resume"])


def analyses():
    for (script, *args), needs in ANALYSES:
        missing = [n for n in needs if not (RAW / n / "manifest.json").exists()]
        if missing:
            print(f"skip {script} {' '.join(args)}: no raw results for {', '.join(missing)} "
                  "(committed summary kept)")
            continue
        run([f"statistics/{script}", *args])


def compare(other):
    """Per-seed result files must be byte-identical; manifests must have the same config."""
    import json
    other_raw = Path(other).resolve() / "results" / "raw"
    bad, checked = [], 0
    for name in CLASSICAL + SENSITIVITY:
        a, b = RAW / name, other_raw / name
        if not (a / "manifest.json").exists() or not (b / "manifest.json").exists():
            bad.append(f"{name}: missing in one checkout")
            continue
        ma, mb = (json.loads((x / "manifest.json").read_text()) for x in (a, b))
        if ma["config"] != mb["config"] or ma["dataset_sha256"] != mb["dataset_sha256"]:
            bad.append(f"{name}: config or dataset hash differs")
        seeds = sorted(p.name for p in a.glob("seed_*.json"))
        if seeds != sorted(p.name for p in b.glob("seed_*.json")):
            bad.append(f"{name}: different seed files")
            continue
        for s in seeds:
            checked += 1
            if (a / s).read_bytes() != (b / s).read_bytes():
                bad.append(f"{name}/{s}: differs")
    print(f"compared {checked} seed files in {len(CLASSICAL + SENSITIVITY)} runs")
    print("\n".join(bad) if bad else "all identical")
    return not bad


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--experiments", action="store_true",
                        help="rerun the classical experiments before the analyses")
    parser.add_argument("--compare", metavar="OTHER_CHECKOUT",
                        help="only compare per-seed results with another checkout")
    args = parser.parse_args(argv)
    if args.compare:
        return 0 if compare(args.compare) else 1
    if args.experiments:
        experiments()
    analyses()
    return 0


if __name__ == "__main__":
    sys.exit(main())
