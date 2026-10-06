"""Pilot of the LLM agents: does the model answer usably, how fast, and does it behave?

    python -m experiments.llm_pilot --domain pharma --model qwen2.5:7b --rounds 10

Plays a few rounds of the baseline and the proposed system on VALIDATION scenarios (never
test scenarios) with one seed. Its output is a feasibility check for sizing and freezing
the LLM protocol; it is not an experimental result and must not be reported as one.
"""
import argparse
import importlib
import json
import platform
import time
from pathlib import Path

import yaml

from agents.llm_agent import OllamaClient
from experiments.llm import simulate_llm, summarise_llm

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ("baseline", "proposed")


def sanity_checks(summaries):
    """Simple behavioural checks; a failed check means the model is unfit, not a finding."""
    checks = {}
    for name, s in summaries.items():
        calls = s["calls"]
        checks[name] = {
            "replies_usable": calls["reports_replaced_by_tool_report"] == 0,
            "votes_not_constant": max(s["vote_share"].values()) < 0.9,
            "confidence_not_constant": 0.02 < s["behaviour"]["mean_confidence"] < 0.98,
        }
    return checks


def run(domain, model, rounds, seed, host):
    prepare = importlib.import_module(f"experiments.{domain}").prepare
    client = OllamaClient(model, host=host)
    out = {"kind": "PILOT - feasibility only, validation scenarios, not an experimental result",
           "domain": domain, "seed": seed, "rounds": rounds, "round_split": "val",
           "model": client.describe(), "python": platform.python_version(), "systems": {},
           "samples": {}}
    prep = None
    for name in SYSTEMS:
        config = yaml.safe_load((ROOT / "configs" / f"{domain}_{name}.yaml").read_text("utf-8"))
        config["game"] = {**config["game"], "n_rounds": rounds, "eval_last": rounds,
                          "round_split": "val"}
        if prep is None:                       # both systems play exactly the same rounds
            prep = prepare(config, seed)
        started = time.perf_counter()
        log, records = simulate_llm(prep, config, seed, client, domain)
        out["systems"][name] = summarise_llm(prep, log, records)
        out["systems"][name]["wall_seconds"] = time.perf_counter() - started
        out["samples"][name] = [r["text"] for r in records[:5]]
    out["sanity_checks"] = sanity_checks(out["systems"])
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--domain", default="pharma", choices=("pharma", "energy"))
    parser.add_argument("--model", required=True, help="Ollama model tag, e.g. qwen2.5:7b")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--output-dir", default=str(ROOT / "results" / "pilot"))
    args = parser.parse_args(argv)

    result = run(args.domain, args.model, args.rounds, args.seed, args.host)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = args.model.replace(":", "_").replace("/", "_")
    path = out_dir / f"llm_pilot_{args.domain}_{tag}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True))
    for name, s in result["systems"].items():
        calls = s["calls"]
        print(f"{name}: {calls['total']} calls, {calls['mean_seconds']:.1f} s/call, "
              f"{calls['unusable_replies']} unusable; votes against tool "
              f"{s['behaviour']['votes_against_tool']:.2f}; vote share {s['vote_share']}")
    print("sanity checks:", json.dumps(result["sanity_checks"]))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
