"""Blockchain provenance layer (Phase 8, protocol amendment 5).

Artifacts (decision, explanation, evidence, reward, reputation of one agent in one round)
stay off-chain. The contract `ProvenanceRegistry.sol` keeps, per record id, the SHA-256
hashes of the three artifacts and reward/reputation scaled by 10^6. Verification recomputes
the hashes from the off-chain store and compares them with the chain.

The chain proves integrity, not truth: a false explanation recorded faithfully is VALID.
"""
import hashlib
import json
import os
import shutil
import socket
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

CONTRACT = Path(__file__).with_name("ProvenanceRegistry.sol")
SOLC_VERSION = "0.8.28"
SCALE = 10 ** 6
UINT32_MAX = 2 ** 32 - 1
VALID, TAMPERED, MISSING = "VALID", "TAMPERED", "MISSING"
RECEIPT_TIMEOUT = 600   # seconds; web3's default of 120 s was once exceeded on a busy machine


# --- hashing ---------------------------------------------------------------------------

def canonical(obj) -> bytes:
    """Canonical JSON: sorted keys, no whitespace, UTF-8; NaN and infinity are refused."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha256(obj) -> bytes:
    return hashlib.sha256(canonical(obj)).digest()


def record_id(run: str, seed: int, system: str, round_: int, agent: str) -> bytes:
    return sha256({"run": run, "seed": seed, "system": system, "round": round_,
                   "agent": agent})


def scaled(x: float) -> int:
    """Reward or reputation as the integer stored on-chain (six decimals)."""
    value = int(round(float(x) * SCALE))
    if not 0 <= value <= UINT32_MAX:
        raise ValueError(f"{x} cannot be stored as uint32 x 1e6")
    return value


def onchain_values(artifact: dict) -> tuple:
    """What the chain stores for an artifact: three hashes, scaled reward and reputation."""
    return (sha256(artifact["decision"]), sha256(artifact["explanation"]),
            sha256(artifact["evidence"]), scaled(artifact["reward"]),
            scaled(artifact["reputation"]))


# --- off-chain artifacts from a saved LLM run --------------------------------------------

def _replies(calls: list) -> dict:
    """The accepted reply of each (round, agent): the last valid attempt."""
    best = {}
    for call in calls:
        if not call["valid"]:
            continue
        key = (call["round"], call["agent"])
        if key not in best or call["attempt"] > best[key]["attempt"]:
            best[key] = call
    return {key: json.loads(call["text"]) for key, call in best.items()}


def artifacts_from_run(result: dict, run: str, agents: tuple) -> dict:
    """Off-chain store {record id hex: artifact} for every system, round and agent."""
    store = {}
    for system, data in result["systems"].items():
        rounds = data["rounds"]
        replies = _replies(data["calls"])
        for t in range(len(rounds["collective"])):
            for i, agent in enumerate(agents):
                if (t, agent) not in replies:
                    raise ValueError(f"no accepted reply for {system} round {t} agent {agent}")
                reply = replies[(t, agent)]
                rid = record_id(run, result["seed"], system, t, agent).hex()
                store[rid] = {
                    "key": {"run": run, "seed": result["seed"], "system": system,
                            "round": t, "agent": agent},
                    "decision": {"vote": int(rounds["votes"][t][i]),
                                 "confidence": float(rounds["confidence"][t][i]),
                                 "collective": int(rounds["collective"][t])},
                    "explanation": {f"{part}_{n}": reply[f"{part}_{n}"]
                                    for n in (1, 2) for part in ("feature", "direction")},
                    "evidence": {f"{part}_{n}": reply[f"{part}_{n}"]
                                 for n in (1, 2) for part in ("feature", "level")},
                    "reward": float(rounds["R"][t][i]),
                    "reputation": float(rounds["reputation"][t][i]),
                }
    return store


# --- tools ------------------------------------------------------------------------------

def find_tool(name: str, env: str, fallback: str) -> str | None:
    """Path of an external tool: environment variable, then PATH, then the documented
    install location of this project's environment."""
    for candidate in (os.environ.get(env), shutil.which(name), fallback):
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def anvil_path():
    return find_tool("anvil", "ANVIL", r"D:\xai-incentive-env\tools\foundry\anvil.exe")


def solc_path():
    return find_tool("solc", "SOLC",
                     rf"D:\xai-incentive-env\tools\solcx\solc-v{SOLC_VERSION}\solc.exe")


def compile_contract(source: Path = CONTRACT) -> dict:
    import solcx
    solc = solc_path()
    if solc is None:
        raise RuntimeError(f"solc {SOLC_VERSION} not found (set SOLC)")
    out = solcx.compile_files([str(source)], output_values=["abi", "bin"],
                              solc_binary=solc, optimize=True, optimize_runs=200)
    (name, compiled), = out.items()
    return {"abi": compiled["abi"], "bytecode": compiled["bin"], "solc": SOLC_VERSION,
            "source": str(source)}


def contract_fingerprint(compiled: dict) -> dict:
    """Identifies exactly which contract was deployed."""
    source = Path(compiled.get("source", CONTRACT))
    return {"source": source.name, "solc": compiled["solc"], "optimizer_runs": 200,
            "source_sha256": hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n"))
            .hexdigest(),
            "creation_bytecode_sha256": hashlib.sha256(
                bytes.fromhex(compiled["bytecode"])).hexdigest()}


def describe_chain(w3) -> dict:
    """Configuration of the local node, as reported by the node itself."""
    info = w3.provider.make_request("anvil_nodeInfo", [])["result"]
    return {"client": w3.client_version, "chain_id": w3.eth.chain_id,
            "hardfork": info["hardFork"], "block_gas_limit": w3.eth.get_block("latest")[
                "gasLimit"], "base_fee_wei": int(info["environment"]["baseFee"], 16),
            "mining": "instant (a block per transaction)", "accounts": "Anvil defaults"}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextmanager
def anvil_node():
    """A fresh local Anvil node (instant mining, default chain settings)."""
    from web3 import Web3
    anvil = anvil_path()
    if anvil is None:
        raise RuntimeError("anvil not found (set ANVIL)")
    port = _free_port()
    proc = subprocess.Popen([anvil, "--port", str(port), "--silent"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        w3 = Web3(Web3.HTTPProvider(f"http://127.0.0.1:{port}"))
        for _ in range(100):
            if w3.is_connected():
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("anvil did not start")
        yield w3
    finally:
        proc.terminate()
        proc.wait(timeout=10)


# --- ledger -----------------------------------------------------------------------------

class Ledger:
    """Client of one deployed ProvenanceRegistry."""

    def __init__(self, w3, compiled: dict):
        self.w3 = w3
        self.owner = w3.eth.accounts[0]
        factory = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
        receipt = w3.eth.wait_for_transaction_receipt(
            factory.constructor().transact({"from": self.owner}), RECEIPT_TIMEOUT)
        self.deploy_gas = receipt["gasUsed"]
        self.contract = w3.eth.contract(address=receipt["contractAddress"],
                                        abi=compiled["abi"])

    def record(self, store: dict, ids: list, batch_size: int = 100) -> list:
        """Write records in batches; returns one entry per transaction."""
        txs = []
        for start in range(0, len(ids), batch_size):
            chunk = ids[start:start + batch_size]
            values = [onchain_values(store[i]) for i in chunk]
            rids = [bytes.fromhex(i) for i in chunk]
            begin = time.perf_counter()
            if batch_size == 1:
                call = self.contract.functions.record(rids[0], *values[0])
            else:
                call = self.contract.functions.recordBatch(rids, *map(list, zip(*values)))
            receipt = self.w3.eth.wait_for_transaction_receipt(
                call.transact({"from": self.owner}), RECEIPT_TIMEOUT)
            seconds = time.perf_counter() - begin
            if receipt["status"] != 1:
                raise RuntimeError("record transaction failed")
            txs.append({"records": len(chunk), "gas": receipt["gasUsed"],
                        "seconds": seconds})
        return txs

    def fetch(self, rid_hex: str):
        from web3.exceptions import ContractLogicError
        try:
            d, e, v, reward, rep, _ = self.contract.functions.get(
                bytes.fromhex(rid_hex)).call()
        except ContractLogicError:
            return None
        return (bytes(d), bytes(e), bytes(v), reward, rep)

    def verify(self, rid_hex: str, artifact: dict) -> str:
        stored = self.fetch(rid_hex)
        if stored is None:
            return MISSING
        return VALID if stored == onchain_values(artifact) else TAMPERED

    def try_write(self, rid_hex: str, artifact: dict, sender=None) -> bool:
        """Attempt a single write; False when the contract refuses it (revert)."""
        from web3.exceptions import ContractLogicError
        try:
            tx = self.contract.functions.record(bytes.fromhex(rid_hex),
                                                *onchain_values(artifact)).transact(
                {"from": sender or self.owner})
        except ContractLogicError:
            return False
        return self.w3.eth.wait_for_transaction_receipt(tx, RECEIPT_TIMEOUT)["status"] == 1
