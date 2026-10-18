"""Blockchain provenance: hashing, artifacts, tampering and the contract on a local EVM."""
import hashlib
import json

import pytest

from blockchain.provenance import (
    MISSING, TAMPERED, VALID, Ledger, anvil_path, anvil_node, artifacts_from_run, canonical,
    compile_contract, onchain_values, record_id, scaled, sha256, solc_path)
from experiments.provenance import TARGETS, reserialise, tamper


def make_result(seed=0, rounds=3, agents=("a", "b")):
    """A tiny run in the format of the saved LLM results (test fixture, not data)."""
    calls = []
    for t in range(rounds):
        for agent in agents:
            reply = {"vote": "candidate_1", "confidence": 0.7, "feature_1": "price",
                     "direction_1": "lowers", "level_1": "low", "feature_2": "delay",
                     "direction_2": "raises", "level_2": "high"}
            calls.append({"round": t, "agent": agent, "attempt": 0, "valid": False,
                          "text": "not json"})
            calls.append({"round": t, "agent": agent, "attempt": 1, "valid": True,
                          "text": json.dumps(reply)})
    log = {"votes": [[1] * len(agents)] * rounds, "confidence": [[0.7] * len(agents)] * rounds,
           "collective": [1] * rounds, "R": [[0.25, 1.0][:len(agents)]] * rounds,
           "reputation": [[0.5] * len(agents)] * rounds}
    return {"seed": seed, "systems": {"proposed": {"calls": calls, "rounds": log}}}


def test_canonical_json_ignores_key_order_and_whitespace():
    a = {"b": 1, "a": {"y": [1, 2], "x": "é"}}
    b = json.loads('{ "a": {"x": "é", "y": [1,2]},\n "b": 1 }')
    assert canonical(a) == canonical(b) == '{"a":{"x":"é","y":[1,2]},"b":1}'.encode()
    assert sha256({}) == hashlib.sha256(b"{}").digest()
    with pytest.raises(ValueError):
        canonical({"x": float("nan")})


def test_record_ids_differ_in_every_field():
    base = ("pharma_llm_main", 0, "proposed", 5, "cost")
    ids = {record_id(*base)}
    for i, other in enumerate(("energy_llm_main", 1, "baseline", 6, "logistics")):
        ids.add(record_id(*base[:i], other, *base[i + 1:]))
    assert len(ids) == 6 and all(len(x) == 32 for x in ids)


def test_scaling_keeps_six_decimals_and_refuses_out_of_range():
    assert scaled(0.2227167) == 222717 and scaled(1.0) == 1_000_000
    assert scaled(0.5 + 1e-6) != scaled(0.5)
    assert scaled(0.5 + 1e-9) == scaled(0.5)        # the declared resolution limit
    # rounding to the nearest unit of 1e-6: under half a unit is invisible, over half is not
    assert scaled(0.5 + 0.4e-6) == 500_000 and scaled(0.5 + 0.6e-6) == 500_001
    assert scaled(0.5 - 0.4e-6) == 500_000 and scaled(0.5 - 0.6e-6) == 499_999
    with pytest.raises(ValueError):
        scaled(-0.1)


def test_meaningful_changes_change_the_hash_formatting_does_not():
    base = {"vote": 2, "confidence": 0.79, "collective": 2}
    assert sha256(base) == sha256(json.loads(json.dumps(base, indent=4)))
    for changed in ({**base, "vote": 3}, {**base, "confidence": 0.7900001},
                    {**base, "confidence": "0.79"}, {**base, "extra": None},
                    {k: v for k, v in base.items() if k != "collective"}):
        assert sha256(changed) != sha256(base)


def test_artifacts_use_the_accepted_reply_of_every_round_and_agent():
    store = artifacts_from_run(make_result(), "run", ("a", "b"))
    assert len(store) == 6
    art = store[record_id("run", 0, "proposed", 2, "b").hex()]
    assert art["key"] == {"run": "run", "seed": 0, "system": "proposed", "round": 2,
                          "agent": "b"}
    assert art["explanation"] == {"feature_1": "price", "direction_1": "lowers",
                                  "feature_2": "delay", "direction_2": "raises"}
    assert art["evidence"]["level_2"] == "high" and art["reward"] == 1.0
    broken = make_result()
    broken["systems"]["proposed"]["calls"] = broken["systems"]["proposed"]["calls"][:-1]
    with pytest.raises(ValueError, match="no accepted reply"):
        artifacts_from_run(broken, "run", ("a", "b"))


@pytest.mark.parametrize("target", TARGETS)
def test_each_tampering_changes_exactly_its_own_on_chain_value(target):
    art = next(iter(artifacts_from_run(make_result(), "run", ("a", "b")).values()))
    before, after = onchain_values(art), onchain_values(tamper(art, target))
    changed = [i for i in range(5) if before[i] != after[i]]
    assert changed == [TARGETS.index(target)]


def test_reserialised_artifact_has_the_same_on_chain_values():
    art = next(iter(artifacts_from_run(make_result(), "run", ("a", "b")).values()))
    again = reserialise(art)
    assert list(again) == list(reversed(list(art)))
    assert onchain_values(again) == onchain_values(art)


chain = pytest.mark.skipif(anvil_path() is None or solc_path() is None,
                           reason="anvil or solc 0.8.28 not installed")


@pytest.fixture(scope="module")
def ledger_store():
    store = artifacts_from_run(make_result(rounds=10), "run", ("a", "b"))
    with anvil_node() as w3:
        ledger = Ledger(w3, compile_contract())
        ids = list(store)
        ledger.record(store, ids[:1], batch_size=1)
        ledger.record(store, ids[1:], batch_size=7)
        yield ledger, store, w3


@chain
def test_recorded_artifacts_verify_and_tampered_ones_do_not(ledger_store):
    ledger, store, _ = ledger_store
    assert ledger.contract.functions.count().call() == len(store)
    for i, art in store.items():
        assert ledger.verify(i, art) == VALID
        assert ledger.verify(i, reserialise(art)) == VALID
    i, art = next(iter(store.items()))
    for target in TARGETS:
        assert ledger.verify(i, tamper(art, target)) == TAMPERED
    assert ledger.verify(i, tamper(art, "reward", delta=1e-9)) == VALID   # below resolution
    assert ledger.verify("ab" * 32, art) == MISSING


@chain
def test_contract_is_append_only_and_owner_only(ledger_store):
    ledger, store, w3 = ledger_store
    i, art = next(iter(store.items()))
    assert not ledger.try_write(i, tamper(art, "explanation"))
    assert ledger.verify(i, art) == VALID
    assert not ledger.try_write("cd" * 32, art, sender=w3.eth.accounts[1])
    assert ledger.verify("cd" * 32, art) == MISSING
    assert ledger.try_write("ef" * 32, art)
    assert ledger.verify("ef" * 32, art) == VALID
