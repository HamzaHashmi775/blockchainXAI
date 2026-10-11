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

from agents.llm_agent import PROMPT_STYLES, OllamaClient
from experiments.llm import simulate_llm, summarise_llm

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ("baseline", "proposed")


def sanity_checks(summaries, prompt_style="disclosed"):
    """Simple behavioural checks; a failed check means the model is unfit, not a finding.

    The reading check only applies when the prompt states the truthful explanation; with
    the raw prompt, working out the explanation is the behaviour under study, not a check.
    """
    checks = {}
    for name, s in summaries.items():
        calls = s["calls"]
        checks[name] = {
            "replies_usable": calls["reports_replaced_by_tool_report"] == 0,
            "votes_not_constant": max(s["vote_share"].values()) < 0.9,
            "confidence_not_constant": 0.02 < s["behaviour"]["mean_confidence"] < 0.98,
            "reads_its_tool": (s["behaviour"]["truthful_explanation_when_voting_with_tool"]
                               or 0.0) >= 0.8
            if name == "proposed" and prompt_style == "disclosed" else None,
        }
    return checks


def run(domain, model, rounds, seed, host, workers=1, prompt_style="disclosed", omega=None):
    prepare = importlib.import_module(f"experiments.{domain}").prepare
    client = OllamaClient(model, host=host)
    out = {"kind": "PILOT - feasibility only, validation scenarios, not an experimental result",
           "domain": domain, "seed": seed, "rounds": rounds, "round_split": "val",
           "workers": workers, "prompt_style": prompt_style,
           "model": client.describe(), "python": platform.python_version(), "systems": {},
           "samples": {}}
    prep = None
    for name in SYSTEMS:
        config = yaml.safe_load((ROOT / "configs" / f"{domain}_{name}.yaml").read_text("utf-8"))
        config["game"] = {**config["game"], "n_rounds": rounds, "eval_last": rounds,
                          "round_split": "val"}
        if omega is not None:
            config["game"]["omega"] = omega
        out["omega"] = config["game"]["omega"]
        if prep is None:                       # both systems play exactly the same rounds
            prep = prepare(config, seed)
        started = time.perf_counter()
        log, records = simulate_llm(prep, config, seed, client, domain, workers=workers,
                                    prompt_style=prompt_style)
        out["systems"][name] = summarise_llm(prep, log, records)
        out["systems"][name]["wall_seconds"] = time.perf_counter() - started
        out["samples"][name] = [{"agent": r["agent"], "prompt": r.get("prompt"),
                                 "reply": r["text"]} for r in records[:5]]
    out["sanity_checks"] = sanity_checks(out["systems"], prompt_style)
    # Ollama cuts a prompt that does not fit silently, so the fit is checked from its counts
    room = client.options["num_ctx"] - client.options["num_predict"]
    for name, s in out["systems"].items():
        longest = s["calls"]["max_prompt_tokens"]
        out["sanity_checks"][name]["prompt_fits_context"] = (
            None if longest is None else longest <= room)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--domain", default="pharma", choices=("pharma", "energy"))
    parser.add_argument("--model", required=True, help="Ollama model tag, e.g. qwen2.5:7b")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--workers", type=int, default=1,
                        help="concurrent requests per round (needs OLLAMA_NUM_PARALLEL)")
    parser.add_argument("--prompt", default="disclosed", choices=PROMPT_STYLES,
                        help="disclosed: truthful explanation stated; raw: numbers only")
    parser.add_argument("--omega", type=float, default=None,
                        help="weight of the private gain in the payoff (default: the config's)")
    parser.add_argument("--tag", default="", help="suffix for the output file name")
    parser.add_argument("--output-dir", default=str(ROOT / "results" / "pilot"))
    args = parser.parse_args(argv)

    result = run(args.domain, args.model, args.rounds, args.seed, args.host,
                 args.workers, args.prompt, args.omega)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = args.model.replace(":", "_").replace("/", "_")
    path = out_dir / f"llm_pilot_{args.domain}_{tag}{args.tag}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True))
    for name, s in result["systems"].items():
        calls = s["calls"]
        print(f"{name}: {calls['total']} calls, {calls['mean_seconds']:.1f} s/call, "
              f"{calls['unusable_replies']} unusable, longest prompt "
              f"{calls['max_prompt_tokens']} tokens; fidelity {s['fidelity']:.2f}, evidence "
              f"{s['evidence_support']:.2f}; votes against tool "
              f"{s['behaviour']['votes_against_tool']:.2f}; vote share {s['vote_share']}")
    print("sanity checks:", json.dumps(result["sanity_checks"]))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
