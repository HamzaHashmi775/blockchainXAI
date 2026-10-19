"""Provenance experiment (Phase 8, H5; protocol amendment 5).

Records the decisions, explanations, evidence, rewards and reputations of the saved LLM main
runs on a local EVM (Anvil), tampers with the off-chain copies and checks detection; measures
the overhead of recording and verifying.

    python experiments/provenance.py --config configs/provenance.yaml
"""
import argparse
import json
import platform
import random
import statistics
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.energy_agents import AGENTS as ENERGY_AGENTS  # noqa: E402
from agents.pharma_agents import AGENTS as PHARMA_AGENTS  # noqa: E402
from blockchain.provenance import (  # noqa: E402
    MISSING, TAMPERED, VALID, Ledger, anvil_node, artifacts_from_run, canonical,
    compile_contract, contract_fingerprint, describe_chain, onchain_values)

AGENTS = {"pharma": PHARMA_AGENTS, "energy": ENERGY_AGENTS}
LEVELS = ("low", "mid", "high")
TARGETS = ("decision", "explanation", "evidence", "reward", "reputation")


def tamper(artifact: dict, target: str, delta: float = 1e-6) -> dict:
    """A copy of the artifact with exactly one field changed."""
    out = json.loads(json.dumps(artifact))
    if target == "decision":
        vote = out["decision"]["vote"]
        out["decision"]["vote"] = vote - 1 if vote > 0 else vote + 1
    elif target == "explanation":
        d = out["explanation"]["direction_1"]
        out["explanation"]["direction_1"] = "lowers" if d == "raises" else "raises"
    elif target == "evidence":
        level = out["evidence"]["level_1"]
        out["evidence"]["level_1"] = LEVELS[(LEVELS.index(level) + 1) % 3] \
            if level in LEVELS else "mid"
    elif target in ("reward", "reputation"):
        out[target] = out[target] + delta
    else:
        raise ValueError(target)
    return out


def reserialise(artifact: dict) -> dict:
    """Same values, keys in reverse order at every level, passed through a different
    textual form (indented JSON)."""
    def flip(obj):
        if isinstance(obj, dict):
            return {k: flip(obj[k]) for k in reversed(list(obj))}
        return obj
    return json.loads(json.dumps(flip(artifact), indent=3))


def load_store(config: dict) -> tuple[dict, list]:
    store, order = {}, []
    for run in config["runs"]:
        domain = run.split("_")[0]
        for seed in config["seeds"]:
            path = ROOT / "results" / "raw" / run / f"seed_{seed}.json"
            part = artifacts_from_run(json.loads(path.read_text()), run, AGENTS[domain])
            store.update(part)
            order.extend(part)
    return store, order


def overhead(compiled: dict, store: dict, ids: list, batch_sizes: list) -> dict:
    out = {}
    for size in batch_sizes:
        with anvil_node() as w3:
            ledger = Ledger(w3, compiled)
            txs = ledger.record(store, ids, batch_size=size)
            begin = time.perf_counter()
            states = [ledger.verify(i, store[i]) for i in ids]
            verify_seconds = time.perf_counter() - begin
        assert states.count(VALID) == len(ids)
        n = len(ids)
        out[str(size)] = {
            "records": n, "transactions": len(txs), "deploy_gas": ledger.deploy_gas,
            "gas_per_record": sum(t["gas"] for t in txs) / n,
            "gas_per_transaction_median": statistics.median(t["gas"] for t in txs),
            "write_seconds_per_record": sum(t["seconds"] for t in txs) / n,
            "write_seconds_per_transaction_median": statistics.median(
                t["seconds"] for t in txs),
            "verify_seconds_per_record": verify_seconds / n,
            "transaction_seconds": [t["seconds"] for t in txs],
        }
    return out


def run(config: dict) -> dict:
    compiled = compile_contract()
    store, order = load_store(config)
    rng = random.Random(config["tampering"]["seed"])
    per_target = config["tampering"]["per_target"]
    n_controls = config["tampering"]["controls"]
    drawn = rng.sample(order, per_target * len(TARGETS) + 2 * n_controls
                       + config["tampering"]["below_resolution"])
    plan, cursor = {}, 0
    for target in TARGETS:
        plan[target] = drawn[cursor:cursor + per_target]
        cursor += per_target
    plan["control_untouched"] = drawn[cursor:cursor + n_controls]
    cursor += n_controls
    plan["control_reserialised"] = drawn[cursor:cursor + n_controls]
    cursor += n_controls
    plan["below_resolution"] = drawn[cursor:]

    # the off-chain store as it is read back for verification, after tampering
    altered = {}
    for target in TARGETS:
        for i in plan[target]:
            altered[i] = tamper(store[i], target)
    for i in plan["control_reserialised"]:
        altered[i] = reserialise(store[i])
    for i in plan["below_resolution"]:
        altered[i] = tamper(store[i], "reward", delta=config["tampering"]["below_delta"])
    path = ROOT / "results" / "raw" / "provenance" / "offchain_store_after_tampering.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({i: altered.get(i, store[i]) for i in order}),
                    encoding="utf-8")
    read_back = json.loads(path.read_text(encoding="utf-8"))

    results = {}
    with anvil_node() as w3:
        chain = describe_chain(w3)
        ledger = Ledger(w3, compiled)
        begin = time.perf_counter()
        txs = ledger.record(store, order, batch_size=config["batch_size"])
        record_seconds = time.perf_counter() - begin
        on_chain = ledger.contract.functions.count().call()
        for group, ids in plan.items():
            states = [ledger.verify(i, read_back[i]) for i in ids]
            results[group] = {s: states.count(s) for s in (VALID, TAMPERED, MISSING)}
        # every record that was not touched must still verify
        untouched = [i for i in order if i not in altered]
        all_states = [ledger.verify(i, read_back[i]) for i in untouched]
        results["all_untouched"] = {s: all_states.count(s) for s in (VALID, TAMPERED, MISSING)}
        # a record that was never written
        results["never_written"] = ledger.verify("00" * 32, store[order[0]])
        # contract rules: no overwrite, no foreign writer
        guard = rng.sample(order, config["contract_checks"])
        results["overwrite_accepted"] = sum(
            ledger.try_write(i, tamper(store[i], "explanation")) for i in guard)
        results["foreign_write_accepted"] = sum(
            ledger.try_write(i[:-8] + "deadbeef", store[i], sender=w3.eth.accounts[1])
            for i in guard)
        results["guard_attempts"] = len(guard)

    detection = {t: results[t][TAMPERED] / per_target for t in TARGETS}
    controls = results["control_untouched"][TAMPERED] + results["control_reserialised"][TAMPERED]
    sizes = [len(canonical(store[i])) for i in order]
    return {
        "protocol": "amendment 5 (v1.5)",
        "config": config,
        "environment": {"python": platform.python_version(), "solc": compiled["solc"],
                        "node": "anvil (Foundry v1.8.5)", "chain": chain,
                        "contract": contract_fingerprint(compiled)},
        "records": len(order), "records_on_chain": on_chain,
        "record_transactions": len(txs),
        "record_gas_total": sum(t["gas"] for t in txs),
        "record_seconds_total": record_seconds,
        "verification": results,
        "detection_rate": detection,
        "detection_rate_all_targets": sum(results[t][TAMPERED] for t in TARGETS)
        / (per_target * len(TARGETS)),
        "false_positive_rate": controls / (2 * n_controls),
        "below_resolution_detected": results["below_resolution"][TAMPERED],
        "offchain_bytes_per_record": statistics.mean(sizes),
        "onchain_storage_bytes_per_record": 4 * 32,
        "overhead": overhead(compiled, store, order[:config["overhead"]["records"]],
                             config["overhead"]["batch_sizes"]),
    }


def _ms(seconds):
    return f"{1000 * seconds:.1f}"


def to_markdown(res: dict) -> str:
    """Table 6 of the paper: everything needed to reproduce and judge the provenance layer."""
    v, cfg, env = res["verification"], res["config"], res["environment"]
    chain, contract = env.get("chain"), env.get("contract")
    lines = [
        "# Table 6 — Blockchain provenance: tamper detection and overhead (H5)",
        "",
        "Protocol amendment 5 (v1.5). Descriptive results; the records are not independent "
        "replications of the agent experiment, and the chain shows integrity, not truth.",
        "",
        "## Set-up",
        "",
        "| Item | Value |",
        "|---|---|",
    ]
    if contract:
        lines += [f"| Contract | `{contract['source']}`, Solidity {contract['solc']}, "
                  f"optimiser {contract['optimizer_runs']} runs |",
                  f"| Contract source SHA-256 | `{contract['source_sha256']}` |",
                  f"| Creation bytecode SHA-256 | `{contract['creation_bytecode_sha256']}` |"]
    else:
        lines.append(f"| Contract | Solidity {env['solc']} |")
    if chain:
        lines += [f"| Node | {chain['client']} (single local node), chain id "
                  f"{chain['chain_id']}, hard fork {chain['hardfork']} |",
                  f"| Blocks | {chain['mining']}; block gas limit "
                  f"{chain['block_gas_limit']:,}; base fee {chain['base_fee_wei']:,} wei |"]
    if env.get("captured_after_run"):
        lines.append(f"| Note | {env['captured_after_run']} |")
    lines += [
        f"| Client | web3.py, Python {env['python']} |",
        "| On-chain per record | record id; SHA-256 of decision, explanation and evidence; "
        "reward and reputation × 10⁶ (uint32); block timestamp |",
        "| Off-chain per record | decision, explanation, evidence, reward, reputation as "
        "canonical JSON |",
        "| Rules | append-only (a record id is written once); only the deploying account "
        "writes |",
        f"| Records | {res['records']:,} = {', '.join(cfg['runs'])}, seeds "
        f"{cfg['seeds'][0]}–{cfg['seeds'][-1]}, 3 systems, 200 rounds, 5 agents; batches of "
        f"{cfg['batch_size']} |",
        "",
        "## Procedure",
        "",
        f"1. All {res['records']:,} records written to a fresh deployment; the off-chain store "
        "saved to disk.",
        f"2. {cfg['tampering']['per_target'] * len(TARGETS):,} records drawn at random (seed "
        f"{cfg['tampering']['seed']}), {cfg['tampering']['per_target']} per target, each "
        "changed in one field of the off-chain store: decision = vote moved to another "
        "option; explanation = direction of feature 1 reversed; evidence = level of feature "
        "1 changed; reward and reputation = +10⁻⁶ (one storage unit).",
        f"3. Controls: {cfg['tampering']['controls']:,} untouched records and "
        f"{cfg['tampering']['controls']:,} re-serialised ones (keys reversed, indented JSON, "
        f"same values). Declared limit: {cfg['tampering']['below_resolution']} rewards "
        f"changed by {cfg['tampering']['below_delta']:g}.",
        "4. The store is read back from disk; each record's hashes and scaled values are "
        "recomputed and compared with the chain (VALID / TAMPERED / MISSING).",
        f"5. Contract rules: {v['guard_attempts']} overwrite attempts and "
        f"{v['guard_attempts']} writes from a second account.",
        f"6. Overhead: the first {cfg['overhead']['records']:,} records of pharma seed 0, on a "
        "fresh deployment for each batch size "
        f"({', '.join(map(str, cfg['overhead']['batch_sizes']))}).",
        "",
        "## Tamper detection",
        "",
        "| Group | Records | VALID | TAMPERED | MISSING | Rate |",
        "|---|---|---|---|---|---|",
    ]
    for group in (*TARGETS, "control_untouched", "control_reserialised", "below_resolution",
                  "all_untouched"):
        c = v[group]
        n = sum(c.values())
        rate = (f"detected {c[TAMPERED] / n:.3f}" if group in (*TARGETS, "below_resolution")
                else f"false positive {c[TAMPERED] / n:.3f}")
        lines.append(f"| {group} | {n:,} | {c[VALID]:,} | {c[TAMPERED]:,} | {c[MISSING]:,} | "
                     f"{rate} |")
    lines += [
        "",
        f"Never-written record: {v['never_written']}. Overwrite attempts accepted: "
        f"{v['overwrite_accepted']} of {v['guard_attempts']}; writes from another account "
        f"accepted: {v['foreign_write_accepted']} of {v['guard_attempts']}. Below-resolution "
        "changes are invisible by design (rounding to the nearest 10⁻⁶).",
        "",
        "## Overhead (local node: excludes consensus, block time and network delay)",
        "",
        "| Batch size | Txs | Gas / record | Gas / tx (median) | Write ms / record (mean) | "
        "Write ms / tx (median) | Verify ms / record |",
        "|---|---|---|---|---|---|---|",
    ]
    for size, o in res["overhead"].items():
        lines.append(
            f"| {size} | {o['transactions']:,} | {o['gas_per_record']:,.0f} | "
            f"{o['gas_per_transaction_median']:,.0f} | {_ms(o['write_seconds_per_record'])} | "
            f"{_ms(o['write_seconds_per_transaction_median'])} | "
            f"{_ms(o['verify_seconds_per_record'])} |")
    o = next(iter(res["overhead"].values()))
    lines += [
        "",
        f"Deployment: {o['deploy_gas']:,} gas. Storage: "
        f"{res['onchain_storage_bytes_per_record']} bytes on-chain per record (4 storage "
        f"slots) against {res['offchain_bytes_per_record']:.0f} bytes of off-chain artifact. "
        f"Full run: {res['record_transactions']:,} transactions, "
        f"{res['record_gas_total']:,} gas ({res['record_gas_total'] / res['records']:,.0f} "
        f"per record), {res['record_seconds_total']:.1f} s.",
        "",
        "Write latency is wall-clock time from sending a transaction to receiving its receipt "
        "and is dominated by the client's receipt polling; gas is the figure that transfers "
        "to other EVM chains.",
    ]
    for note in res.get("notes", []):
        lines += ["", f"Note: {note}"]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(ROOT / "configs" / "provenance.yaml"))
    parser.add_argument("--table-only", action="store_true",
                        help="re-render the table from results/summaries/provenance.json")
    args = parser.parse_args(argv)
    summary = ROOT / "results" / "summaries" / "provenance.json"
    if args.table_only:
        res = json.loads(summary.read_text(encoding="utf-8"))
    else:
        config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
        res = run(config)
        summary.write_text(json.dumps(res, indent=2), encoding="utf-8")
    text = to_markdown(res)
    (ROOT / "tables" / "provenance.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
