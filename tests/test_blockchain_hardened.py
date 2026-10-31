"""Hardened provenance (amendment 9): Merkle trees, identities, signatures, forgery, rewrite."""
import hashlib

import pytest

from blockchain.hardened import (
    AgentIdentity, AnchorChain, HardenedLedger, agent_id, compile_hardened, leaf_hash,
    merkle_proof, merkle_root, model_identity, node_hash, record_leaf, signed_digest,
    derived_account, verify_proof)
from blockchain.provenance import (
    MISSING, TAMPERED, VALID, anvil_node, anvil_path, artifacts_from_run, onchain_values,
    sha256, solc_path)
from experiments.provenance import TARGETS, tamper
from experiments.provenance_hardened import (
    audit, owner_of, substituted_model, write_and_anchor)
from tests.test_blockchain import make_result

LLM = {"model": "m", "digest": "ab" * 32, "temperature": 0.0, "num_ctx": 2048,
       "num_predict": 120, "prompt_style": "raw"}


def leaves(n):
    return [leaf_hash(bytes([i])) for i in range(n)]


def test_merkle_root_matches_rfc6962_shape():
    l3 = leaves(3)
    assert merkle_root(l3[:1]) == l3[0]
    assert merkle_root(l3) == node_hash(node_hash(l3[0], l3[1]), l3[2])
    l5 = leaves(5)
    assert merkle_root(l5) == node_hash(merkle_root(l5[:4]), l5[4])
    assert leaf_hash(b"") == hashlib.sha256(b"\x00").digest()
    with pytest.raises(ValueError):
        merkle_root([])


@pytest.mark.parametrize("n", range(1, 18))
def test_every_proof_verifies_and_wrong_ones_do_not(n):
    ls = leaves(n)
    root = merkle_root(ls)
    for k in range(n):
        proof = merkle_proof(ls, k)
        assert verify_proof(ls[k], k, n, proof, root)
        assert not verify_proof(leaf_hash(b"other"), k, n, proof, root)
        if n > 1:
            assert not verify_proof(ls[k], (k + 1) % n, n, proof, root)
            assert not verify_proof(ls[k], k, n, proof[:-1], root)
    assert not verify_proof(ls[0], n, n, [], root)


def test_identities_are_deterministic_and_bind_the_model():
    a = derived_account("pharma", "cost")
    assert a.address == derived_account("pharma", "cost").address
    assert a.address != derived_account("pharma", "reliability").address
    assert a.address != derived_account("pharma", "cost", "amendment-9 operator key").address
    assert agent_id("pharma", "cost") != agent_id("energy", "cost")
    ident = AgentIdentity("pharma", "cost", a, model_identity(LLM, "You gain on price."))
    assert ident.model_hash == sha256({**LLM, "objective": "You gain on price."})


@pytest.mark.parametrize("kind", ["digest", "objective", "temperature"])
def test_each_model_substitution_changes_the_model_hash(kind):
    from agents.llm_agent import OBJECTIVES
    ident = AgentIdentity("pharma", "cost", derived_account("pharma", "cost"),
                          model_identity(LLM, OBJECTIVES["pharma"]["cost"]))
    changed = substituted_model(ident, kind)
    assert sha256(changed) != ident.model_hash
    assert [k for k in changed if changed[k] != ident.model[k]] == [
        {"digest": "digest", "objective": "objective", "temperature": "temperature"}[kind]]


def test_record_leaf_changes_with_every_on_chain_value():
    values = (b"\x01" * 32, b"\x02" * 32, b"\x03" * 32, 5, 6)
    base = record_leaf(b"\x00" * 32, b"\x09" * 32, values)
    for k in range(5):
        changed = list(values)
        changed[k] = changed[k] + 1 if k >= 3 else b"\x07" * 32
        assert record_leaf(b"\x00" * 32, b"\x09" * 32, tuple(changed)) != base
    assert record_leaf(b"\x08" * 32, b"\x09" * 32, values) != base


chain = pytest.mark.skipif(anvil_path() is None or solc_path() is None,
                           reason="anvil or solc 0.8.28 not installed")


@pytest.fixture(scope="module")
def setting():
    store = artifacts_from_run(make_result(rounds=6), "run", ("a", "b"))
    order = list(store)
    idents = {("run", x): AgentIdentity("run", x, derived_account("run", x), {"m": x})
              for x in ("a", "b")}
    config = {"anchor_every": 5, "batch_size": 3}
    compiled, anchor_compiled = compile_hardened()
    with anvil_node() as anchor_w3, anvil_node() as w3:
        anchors = AnchorChain(anchor_w3, anchor_compiled)
        ledger = HardenedLedger(w3, compiled)
        kept = write_and_anchor(ledger, anchors, store, order, idents, config)
        yield {"store": store, "order": order, "idents": idents, "config": config,
               "compiled": compiled, "anchors": anchors, "ledger": ledger, "kept": kept,
               "w3": w3}


@chain
def test_python_digest_equals_the_contract_digest(setting):
    ledger = setting["ledger"]
    args = [b"\x01" * 32, b"\x02" * 32, b"\x03" * 32, b"\x04" * 32, b"\x05" * 32, b"\x06" * 32]
    assert bytes(ledger.contract.functions.digest(*args).call()) == signed_digest(
        ledger.chain_id, ledger.address, *args)


@chain
def test_honest_run_audits_clean(setting):
    s = setting
    assert s["anchors"].size() == 1 + 3            # registration + 12 records / 5 per anchor
    result = audit(s["ledger"], s["anchors"], s["store"], s["order"], s["idents"], s["kept"])
    assert result["per_record"] == {VALID: 12, TAMPERED: 0, MISSING: 0}
    assert result["registrations_mismatched"] == 0 and result["anchors_mismatched"] == 0
    assert result["records_failing_anchor"] == set()
    i = s["order"][0]
    assert s["ledger"].verify(bytes.fromhex(i), tamper(s["store"][i], "decision")) == TAMPERED


@chain
def test_forged_and_replayed_records_are_refused(setting):
    s = setting
    ledger, w3 = s["ledger"], s["w3"]
    i = s["order"][0]
    ident, art = s["idents"][owner_of(s["store"][i])], s["store"][i]
    other = s["idents"][("run", "b" if ident.agent == "a" else "a")]
    second = HardenedLedger(w3, s["compiled"])
    second.register(list(s["idents"].values()))
    fresh = iter(sha256({"t": k}) for k in range(20))
    cases = {
        "bad signature": [
            ledger.entry(next(fresh), ident, art, change_explanation=True),
            ledger.entry(next(fresh), ident, art, signer=other.account),
            ledger.entry(next(fresh), ident, art, signer=derived_account("x", "y")),
            ledger.entry(next(fresh), ident, art, signed_rid=b"\x0f" * 32),
            ledger.entry(next(fresh), ident, art,
                         signed_for=(second.chain_id, second.address))],
        "model mismatch": [ledger.entry(next(fresh), ident, art, model_hash=b"\x0e" * 32)],
        "record exists": [ledger.entry(bytes.fromhex(i), ident, art)],
    }
    for reason, entries in cases.items():
        for entry in entries:
            assert ledger.try_write(entry) == (False, reason)
    valid = ledger.entry(next(fresh), ident, art)
    assert ledger.try_write(valid, sender=w3.eth.accounts[1]) == (False, "not owner")
    assert ledger.try_write(valid) == (True, None)
    # the same signature is valid on the second deployment only for that deployment
    assert second.try_write(second.entry(next(fresh), ident, art)) == (True, None)


@chain
def test_rewritten_history_is_found_by_registration_and_anchors(setting):
    s = setting
    order, store = s["order"], s["store"]
    altered = dict(store)
    changed = {order[1]: "decision", order[7]: "reward"}
    for i, target in changed.items():
        altered[i] = tamper(store[i], target)
    with anvil_node() as w3:
        forged = HardenedLedger(w3, s["compiled"])
        operator = {k: AgentIdentity(a.domain, a.agent, derived_account(a.domain, a.agent, "op"),
                                     a.model) for k, a in s["idents"].items()}
        forged.register(list(operator.values()))
        forged.write([forged.entry(bytes.fromhex(i), operator[owner_of(altered[i])],
                                   altered[i]) for i in order], 4)
        result = audit(forged, s["anchors"], altered, order, s["idents"], s["kept"])
    assert result["per_record"][VALID] == len(order)        # store and chain agree
    assert result["registrations_mismatched"] == 2           # but the keys are not the agents'
    assert result["records_failing_anchor"] == set(changed)  # and exactly the changes show
    assert result["anchors_mismatched"] == 2                 # records 1 and 7: blocks 0 and 1


def test_tamper_targets_cover_every_on_chain_value():
    art = next(iter(artifacts_from_run(make_result(), "run", ("a", "b")).values()))
    assert {i for t in TARGETS for i in range(5)
            if onchain_values(tamper(art, t))[i] != onchain_values(art)[i]} == set(range(5))
