"""Hardened provenance experiment (protocol amendment 9).

Same 30,000 records as amendment 5, written to `ProvenanceRegistryV2` (agent signatures,
model registration) with Merkle anchors on a second local node. Tests forgery and replay at
write time, a history rewrite by the operator, and the overhead.

    python experiments/provenance_hardened.py --config configs/provenance_hardened.yaml
"""
import argparse
import hashlib
import json
import platform
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.energy_agents import AGENTS as ENERGY_AGENTS  # noqa: E402
from agents.llm_agent import OBJECTIVES  # noqa: E402
from agents.pharma_agents import AGENTS as PHARMA_AGENTS  # noqa: E402
from blockchain.hardened import (  # noqa: E402
    AgentIdentity, AnchorChain, HardenedLedger, anchor_label, compile_hardened, merkle_proof,
    merkle_root, model_identity, record_leaf, registration_leaf, derived_account, verify_proof)
from blockchain.provenance import (  # noqa: E402
    MISSING, TAMPERED, VALID, Ledger, anvil_node, compile_contract, contract_fingerprint,
    describe_chain, onchain_values, sha256)
from experiments.provenance import TARGETS, load_store, tamper  # noqa: E402

AGENTS = {"pharma": PHARMA_AGENTS, "energy": ENERGY_AGENTS}
def log(message: str) -> None:
    """Progress line with a timestamp (stdout), to diagnose a stalled node."""
    print(time.strftime("%H:%M:%S"), message, flush=True)


ATTACKS = ("content_changed_after_signing", "other_agents_key", "unregistered_key",
           "replay_other_record_id", "replay_other_deployment", "model_substituted",
           "non_owner_sender")


def identities(config: dict, label: str = "amendment-9 test key") -> dict:
    """{(domain, agent): AgentIdentity}, model identity from each run's manifest."""
    out = {}
    for run in config["runs"]:
        domain = run.split("_")[0]
        manifest = json.loads((ROOT / "results" / "raw" / run / "manifest.json").read_text())
        for agent in AGENTS[domain]:
            out[(domain, agent)] = AgentIdentity(
                domain, agent, derived_account(domain, agent, label),
                model_identity(manifest["config"]["llm"], OBJECTIVES[domain][agent]))
    return out


def owner_of(artifact: dict) -> tuple:
    return artifact["key"]["run"].split("_")[0], artifact["key"]["agent"]


def substituted_model(ident: AgentIdentity, kind: str) -> dict:
    model = dict(ident.model)
    if kind == "digest":
        model["digest"] = hashlib.sha256(b"substituted model").hexdigest()
    elif kind == "objective":
        agents = AGENTS[ident.domain]
        other = agents[(agents.index(ident.agent) + 1) % len(agents)]
        model["objective"] = OBJECTIVES[ident.domain][other]
    elif kind == "temperature":
        model["temperature"] = model["temperature"] + 0.7
    else:
        raise ValueError(kind)
    return model


def registration_leaves(idents: list, registered=None) -> list:
    """Leaves in fixed agent order; from the identities, or as a ledger reports them."""
    leaves = []
    for ident in idents:
        key, model_hash = (registered(ident.id) if registered
                           else (ident.account.address, ident.model_hash))
        leaves.append(registration_leaf(ident.id, key, model_hash))
    return leaves


def write_and_anchor(ledger, anchors, store, order, idents, config) -> dict:
    """Register, anchor the registrations, sign and write every record, anchor every block.
    Returns timings, gas and the inclusion proofs kept off-chain."""
    reg_gas = ledger.register(list(idents.values()))
    reg_leaves = registration_leaves(list(idents.values()))
    anchor_gas = [anchors.anchor(anchor_label("registration"), merkle_root(reg_leaves),
                                 len(reg_leaves))]
    reg_proofs = [merkle_proof(reg_leaves, k) for k in range(len(reg_leaves))]
    every, txs, proofs, sign_seconds = config["anchor_every"], [], {}, 0.0
    for block, start in enumerate(range(0, len(order), every)):
        ids = order[start:start + every]
        begin = time.perf_counter()
        entries = [ledger.entry(bytes.fromhex(i), idents[owner_of(store[i])], store[i])
                   for i in ids]
        sign_seconds += time.perf_counter() - begin
        txs += ledger.write(entries, config["batch_size"])
        leaves = [record_leaf(bytes.fromhex(i), idents[owner_of(store[i])].id,
                              onchain_values(store[i])) for i in ids]
        anchor_gas.append(anchors.anchor(anchor_label("records", block), merkle_root(leaves),
                                         len(leaves)))
        for k, i in enumerate(ids):
            proofs[i] = (block, k, len(ids), merkle_proof(leaves, k))
    return {"registration_gas": reg_gas, "anchor_gas": anchor_gas, "txs": txs,
            "sign_seconds": sign_seconds, "proofs": proofs, "registration_proofs": reg_proofs}


def audit(ledger, anchors, store_view, order, idents, kept) -> dict:
    """What an auditor finds: per-record verification against the off-chain store, the
    registrations and each record checked against the anchored roots."""
    agents = list(idents.values())
    anchored = [anchors.get(k) for k in range(anchors.size())]
    _, reg_root, n_reg = anchored[0]
    reg_now = registration_leaves(agents, ledger.registered)
    reg_bad = sum(not verify_proof(leaf, k, n_reg, kept["registration_proofs"][k], reg_root)
                  for k, leaf in enumerate(reg_now))
    states, failing, leaves_by_block = Counter(), set(), {}
    for i in order:
        rid = bytes.fromhex(i)
        stored = ledger.fetch(rid)
        if stored is None:
            states[MISSING] += 1
            failing.add(i)
            continue
        aid, values = stored
        states[VALID if values == onchain_values(store_view[i]) else TAMPERED] += 1
        block, k, n, proof = kept["proofs"][i]
        leaf = record_leaf(rid, aid, values)
        leaves_by_block.setdefault(block, []).append(leaf)
        if not verify_proof(leaf, k, n, proof, anchored[1 + block][1]):
            failing.add(i)
    roots_bad = sum(merkle_root(leaves) != anchored[1 + block][1]
                    for block, leaves in leaves_by_block.items())
    return {"per_record": {s: states[s] for s in (VALID, TAMPERED, MISSING)},
            "registrations_mismatched": reg_bad, "registrations": len(agents),
            "anchors_mismatched": roots_bad, "anchors": len(leaves_by_block),
            "records_failing_anchor": failing}


def fresh_id(kind: str, n: int, rid_hex: str) -> bytes:
    return sha256({"attack": kind, "n": n, "of": rid_hex})


def forgery(w3, ledger, compiled, store, idents, rng, order, config) -> dict:
    """A9.2 step 2: every attempt uses a fresh record id; returns accepted counts and reasons."""
    n = config["forgery_attempts"]
    agents = list(idents.values())
    stranger = derived_account("none", "none", "amendment-9 unregistered key")
    second = HardenedLedger(w3, compiled)
    second.register(agents)
    kinds = config["model_substitutions"]
    out = {}
    for kind in ("valid_control", *ATTACKS):
        accepted, reasons = 0, Counter()
        for k, i in enumerate(rng.sample(order, n)):
            ident, art = idents[owner_of(store[i])], store[i]
            rid = fresh_id(kind, k, i)
            sender = None
            if kind == "valid_control":
                entry = ledger.entry(rid, ident, art)
            elif kind == "content_changed_after_signing":
                entry = ledger.entry(rid, ident, art, change_explanation=True)
            elif kind == "other_agents_key":
                other = rng.choice([a for a in agents if a is not ident])
                entry = ledger.entry(rid, ident, art, signer=other.account)
            elif kind == "unregistered_key":
                entry = ledger.entry(rid, ident, art, signer=stranger)
            elif kind == "replay_other_record_id":
                entry = ledger.entry(rid, ident, art, signed_rid=fresh_id("signed", k, i))
            elif kind == "replay_other_deployment":
                entry = ledger.entry(rid, ident, art,
                                     signed_for=(second.chain_id, second.address))
            elif kind == "model_substituted":
                model = substituted_model(ident, kinds[k % len(kinds)])
                entry = ledger.entry(rid, ident, art, model_hash=sha256(model))
            elif kind == "non_owner_sender":
                entry = ledger.entry(rid, ident, art)
                sender = w3.eth.accounts[1]
            ok, reason = ledger.try_write(entry, sender=sender)
            accepted += ok
            reasons[reason or "accepted"] += 1
        out[kind] = {"attempts": n, "accepted": accepted, "outcomes": dict(reasons)}
    return out


def overhead(compiled, anchor_compiled, store, ids, idents, batch_sizes) -> dict:
    out = {}
    pharma = [a for (d, _), a in idents.items() if d == "pharma"]
    for size in batch_sizes:
        with anvil_node() as w3:
            ledger = HardenedLedger(w3, compiled)
            ledger.register(pharma)
            begin = time.perf_counter()
            entries = [ledger.entry(bytes.fromhex(i), idents[owner_of(store[i])], store[i])
                       for i in ids]
            sign_seconds = time.perf_counter() - begin
            txs = ledger.write(entries, size)
            begin = time.perf_counter()
            states = [ledger.verify(bytes.fromhex(i), store[i]) for i in ids]
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
            "sign_seconds_per_record": sign_seconds / n,
            "verify_seconds_per_record": verify_seconds / n,
        }
    leaves = [record_leaf(bytes.fromhex(i), idents[owner_of(store[i])].id,
                          onchain_values(store[i])) for i in ids]
    begin = time.perf_counter()
    root = merkle_root(leaves)
    tree_seconds = time.perf_counter() - begin
    proofs = [merkle_proof(leaves, k) for k in range(len(leaves))]
    begin = time.perf_counter()
    assert all(verify_proof(leaf, k, len(leaves), p, root)
               for k, (leaf, p) in enumerate(zip(leaves, proofs)))
    proof_verify = (time.perf_counter() - begin) / len(leaves)
    with anvil_node() as w3:
        anchors = AnchorChain(w3, anchor_compiled)
        anchor_gas = anchors.anchor(anchor_label("records", 0), root, len(leaves))
    sizes = [32 * len(p) for p in proofs]
    return {"batches": out, "anchor": {
        "leaves": len(leaves), "anchor_deploy_gas": anchors.deploy_gas,
        "anchor_gas": anchor_gas, "tree_seconds": tree_seconds,
        "proof_bytes_median": statistics.median(sizes), "proof_bytes_max": max(sizes),
        "proof_verify_seconds": proof_verify}}


def run(config: dict) -> dict:
    compiled, anchor_compiled = compile_hardened()
    v1 = compile_contract()
    store, order = load_store(config)
    idents = identities(config)
    rng = random.Random(config["rng_seed"])
    timing = {}

    # A9.2 step 3 plan, drawn first so that it does not depend on the forgery draws
    altered_ids = rng.sample(order, config["rewrite"]["per_target"] * len(TARGETS))
    altered = dict(store)
    per = config["rewrite"]["per_target"]
    for t, target in enumerate(TARGETS):
        for i in altered_ids[t * per:(t + 1) * per]:
            altered[i] = tamper(store[i], target)

    res = {}
    with anvil_node() as anchor_w3:
        anchors = AnchorChain(anchor_w3, anchor_compiled)
        with anvil_node() as w3:
            chain = describe_chain(w3)
            ledger = HardenedLedger(w3, compiled)
            begin = time.perf_counter()
            log("honest run: writing and anchoring")
            kept = write_and_anchor(ledger, anchors, store, order, idents, config)
            timing["honest_write_seconds"] = time.perf_counter() - begin
            log("honest run: audit")
            honest = audit(ledger, anchors, store, order, idents, kept)
            res["honest"] = {**honest, "records_failing_anchor": len(
                honest["records_failing_anchor"])}
            res["records_on_chain"] = ledger.contract.functions.count().call()
            log("forgery and replay attempts")
            res["forgery"] = forgery(w3, ledger, compiled, store, idents, rng, order, config)
            honest_gas = {"deploy": ledger.deploy_gas,
                          "registration": kept["registration_gas"],
                          "records": sum(t["gas"] for t in kept["txs"]),
                          "transactions": len(kept["txs"]),
                          "anchors": len(kept["anchor_gas"]),
                          "anchor_gas_total": sum(kept["anchor_gas"]),
                          "sign_seconds": kept["sign_seconds"]}

        # step 3: the operator rebuilds the chain from the altered store
        with anvil_node() as w3:
            log("rewrite: amendment-5 contract")
            old = Ledger(w3, v1)
            old.record(altered, order, batch_size=config["batch_size"])
            states = Counter(old.verify(i, altered[i]) for i in altered_ids)
            res["rewrite_amendment5"] = {s: states[s] for s in (VALID, TAMPERED, MISSING)}
        with anvil_node() as w3:
            log("rewrite: hardened contract")
            forged = HardenedLedger(w3, compiled)
            operator_idents = {k: AgentIdentity(a.domain, a.agent,
                                                derived_account(a.domain, a.agent,
                                                             "amendment-9 operator key"),
                                                a.model)
                               for k, a in idents.items()}
            forged.register(list(operator_idents.values()))
            entries = [forged.entry(bytes.fromhex(i), operator_idents[owner_of(altered[i])],
                                    altered[i]) for i in order]
            forged.write(entries, config["batch_size"])
            rewrite = audit(forged, anchors, altered, order, idents, kept)
        failing = rewrite["records_failing_anchor"]
        altered_set = set(altered_ids)
        res["rewrite_hardened"] = {
            **{k: v for k, v in rewrite.items() if k != "records_failing_anchor"},
            "altered": len(altered_ids),
            "altered_detected_by_anchor": len(failing & altered_set),
            "altered_detected_by_target": {
                target: len(failing & set(altered_ids[t * per:(t + 1) * per]))
                for t, target in enumerate(TARGETS)},
            "unaltered_flagged": len(failing - altered_set),
            "unaltered": len(order) - len(altered_ids),
        }
        res["anchors_on_chain"] = anchors.size()

    log("overhead")
    cost = overhead(compiled, anchor_compiled, store, order[:config["overhead"]["records"]],
                    idents, config["overhead"]["batch_sizes"])
    log("done")
    return {
        "protocol": "amendment 9 (v1.9)",
        "config": config,
        "environment": {"python": platform.python_version(), "solc": compiled["solc"],
                        "node": "anvil (Foundry v1.8.5)", "chain": chain,
                        "contracts": [contract_fingerprint(compiled),
                                      contract_fingerprint(anchor_compiled)]},
        "records": len(order),
        "agents": {f"{d}/{a}": {"agent_id": i.id.hex(), "key": i.account.address,
                                "model_hash": i.model_hash.hex(), "model": i.model}
                   for (d, a), i in idents.items()},
        "gas": honest_gas,
        "timing": timing,
        **res,
        "overhead": cost,
    }


def _ms(seconds):
    return f"{1000 * seconds:.1f}"


def to_markdown(res: dict, v1: dict | None) -> str:
    cfg, h, rw = res["config"], res["honest"], res["rewrite_hardened"]
    old = res["rewrite_amendment5"]
    lines = [
        "# Table 6b — Hardened provenance: signatures, model registration, anchoring",
        "",
        "Protocol amendment 9 (v1.9), added post hoc; descriptive. The external chain is "
        "simulated by a second local Anvil node; agent keys are deterministic test keys. "
        "Integrity, not truth: a signed, anchored record can still hold a false explanation.",
        "",
        "## Honest run (false-positive check)",
        "",
        f"{res['records']:,} records ({', '.join(cfg['runs'])}, seeds {cfg['seeds'][0]}–"
        f"{cfg['seeds'][-1]}), {len(res['agents'])} registered agents, "
        f"{res['anchors_on_chain']} anchors (1 registration + one per "
        f"{cfg['anchor_every']:,} records).",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Per-record verification | VALID {h['per_record'][VALID]:,}, TAMPERED "
        f"{h['per_record'][TAMPERED]:,}, MISSING {h['per_record'][MISSING]:,} |",
        f"| Registrations differing from anchor | {h['registrations_mismatched']} of "
        f"{h['registrations']} |",
        f"| Anchored roots differing | {h['anchors_mismatched']} of {h['anchors']} |",
        f"| Records failing their inclusion proof | {h['records_failing_anchor']:,} |",
        "",
        "## Forgery and replay (refused at write time)",
        "",
        f"{cfg['forgery_attempts']} attempts each, fresh record ids, records drawn at random.",
        "",
        "| Attempt | Accepted | Outcome |",
        "|---|---|---|",
    ]
    for kind, r in res["forgery"].items():
        outcome = ", ".join(f"{k}: {v}" for k, v in sorted(r["outcomes"].items()))
        lines.append(f"| {kind} | {r['accepted']} of {r['attempts']} | {outcome} |")
    lines += [
        "",
        "## History rewrite by the operator",
        "",
        f"{rw['altered']} records altered ({cfg['rewrite']['per_target']} per target) and the "
        f"whole chain rebuilt on a fresh node, consistent with the altered off-chain store.",
        "",
        "| Check | Amendment-5 contract | Hardened + anchors |",
        "|---|---|---|",
        f"| Records flagged by per-record verification | {old[TAMPERED]} of "
        f"{rw['altered']} | {rw['per_record'][TAMPERED]} of {res['records']:,} |",
        f"| Registrations differing from anchor (operator's own keys) | – | "
        f"{rw['registrations_mismatched']} of {rw['registrations']} |",
        f"| Anchored roots differing | – | {rw['anchors_mismatched']} of {rw['anchors']} |",
        f"| Altered records failing their inclusion proof | – | "
        f"{rw['altered_detected_by_anchor']} of {rw['altered']} |",
        f"| Unaltered records failing their inclusion proof | – | "
        f"{rw['unaltered_flagged']} of {rw['unaltered']:,} |",
        "",
        "Altered records detected by anchor, per target: "
        + ", ".join(f"{t} {n}/{cfg['rewrite']['per_target']}"
                    for t, n in rw["altered_detected_by_target"].items()) + ".",
        "",
        "## Overhead (local node: excludes consensus, block time and network delay)",
        "",
        "| Batch size | Gas / record | Amendment 5 gas / record | Write ms / tx (median) | "
        "Sign ms / record | Verify ms / record |",
        "|---|---|---|---|---|---|",
    ]
    for size, o in res["overhead"]["batches"].items():
        base = f"{v1['overhead'][size]['gas_per_record']:,.0f}" if v1 else "–"
        lines.append(f"| {size} | {o['gas_per_record']:,.0f} | {base} | "
                     f"{_ms(o['write_seconds_per_transaction_median'])} | "
                     f"{_ms(o['sign_seconds_per_record'])} | "
                     f"{_ms(o['verify_seconds_per_record'])} |")
    a, g = res["overhead"]["anchor"], res["gas"]
    lines += [
        "",
        f"Deployment {g['deploy']:,} gas; registering {len(res['agents'])} agents "
        f"{g['registration']:,} gas. Anchoring: {a['anchor_gas']:,} gas per anchor "
        f"({a['leaves']:,} records; {a['anchor_gas'] / a['leaves']:,.0f} gas per record); "
        f"tree of {a['leaves']:,} leaves built in {_ms(a['tree_seconds'])} ms; inclusion "
        f"proof {a['proof_bytes_median']:.0f} bytes (max {a['proof_bytes_max']}), verified "
        f"in {1e6 * a['proof_verify_seconds']:.0f} µs. Full run: {g['transactions']:,} "
        f"transactions, {g['records']:,} gas ({g['records'] / res['records']:,.0f} per "
        f"record), signing {g['sign_seconds']:.0f} s in total.",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(ROOT / "configs" / "provenance_hardened.yaml"))
    parser.add_argument("--table-only", action="store_true",
                        help="re-render the table from the saved summary")
    args = parser.parse_args(argv)
    summary = ROOT / "results" / "summaries" / "provenance_hardened.json"
    if args.table_only:
        res = json.loads(summary.read_text(encoding="utf-8"))
    else:
        config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
        res = run(config)
        summary.write_text(json.dumps(res, indent=2), encoding="utf-8")
    v1_path = ROOT / "results" / "summaries" / "provenance.json"
    v1 = json.loads(v1_path.read_text(encoding="utf-8")) if v1_path.exists() else None
    text = to_markdown(res, v1)
    (ROOT / "tables" / "provenance_hardened.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
