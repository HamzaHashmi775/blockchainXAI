"""Hardened provenance layer (protocol amendment 9).

Adds to `blockchain.provenance` (amendment 5):
- model registration: each agent id is bound once to a signing key and a model hash;
- agent signatures: the contract accepts a record only if the agent's registered key signed
  it for this chain and this contract;
- anchoring: Merkle roots (RFC 6962) of the registrations and of every block of records are
  written to `AnchorRegistry` on a second chain, so a rewritten history can be detected.

The agent keys made here are test keys derived from public strings; they are not secrets.
"""
import hashlib
from dataclasses import dataclass
from pathlib import Path

from blockchain.provenance import (
    MISSING, RECEIPT_TIMEOUT, TAMPERED, VALID, compile_contract, onchain_values, sha256)

HERE = Path(__file__).resolve().parent
REGISTRY_V2 = HERE / "ProvenanceRegistryV2.sol"
ANCHOR = HERE / "AnchorRegistry.sol"


# --- identities -------------------------------------------------------------------------

def agent_id(domain: str, agent: str) -> bytes:
    return sha256({"domain": domain, "agent": agent})


def derived_account(domain: str, agent: str, label: str = "amendment-9 test key"):
    """A deterministic secp256k1 test key (not a secret: derived from public strings)."""
    from eth_account import Account
    return Account.from_key(hashlib.sha256(f"{label}|{domain}|{agent}".encode()).digest())


def model_identity(llm: dict, objective: str) -> dict:
    """What a model hash commits to: the model, its decoding settings and the agent's role."""
    return {"model": llm["model"], "digest": llm["digest"],
            "temperature": llm["temperature"], "num_ctx": llm["num_ctx"],
            "num_predict": llm["num_predict"], "prompt_style": llm["prompt_style"],
            "objective": objective}


@dataclass
class AgentIdentity:
    domain: str
    agent: str
    account: object
    model: dict

    @property
    def id(self) -> bytes:
        return agent_id(self.domain, self.agent)

    @property
    def model_hash(self) -> bytes:
        return sha256(self.model)


# --- signatures -------------------------------------------------------------------------

def signed_digest(chain_id: int, contract: str, rid: bytes, aid: bytes, d: bytes, e: bytes,
                  v: bytes, model_hash: bytes) -> bytes:
    """keccak256(abi.encode(...)) exactly as `ProvenanceRegistryV2.digest`."""
    from eth_abi import encode
    from eth_utils import keccak
    return keccak(encode(["uint256", "address"] + ["bytes32"] * 6,
                         [chain_id, contract, rid, aid, d, e, v, model_hash]))


def sign(account, digest: bytes) -> bytes:
    """EIP-191 signature (65 bytes, r ‖ s ‖ v) of a 32-byte digest."""
    from eth_account.messages import encode_defunct
    return bytes(account.sign_message(encode_defunct(primitive=digest)).signature)


# --- Merkle tree (RFC 6962) -------------------------------------------------------------

def leaf_hash(data: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + data).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def _split(n: int) -> int:
    """Largest power of two smaller than n (n > 1)."""
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def merkle_root(leaves: list) -> bytes:
    """Root over leaf hashes."""
    if not leaves:
        raise ValueError("empty tree")
    if len(leaves) == 1:
        return leaves[0]
    k = _split(len(leaves))
    return node_hash(merkle_root(leaves[:k]), merkle_root(leaves[k:]))


def merkle_proof(leaves: list, index: int) -> list:
    """Audit path of leaf `index`, deepest sibling first."""
    if len(leaves) == 1:
        return []
    k = _split(len(leaves))
    if index < k:
        return merkle_proof(leaves[:k], index) + [merkle_root(leaves[k:])]
    return merkle_proof(leaves[k:], index - k) + [merkle_root(leaves[:k])]


def root_from_proof(leaf: bytes, index: int, n: int, proof: list) -> bytes:
    if not 0 <= index < n:
        raise ValueError("index out of range")
    if n == 1:
        if proof:
            raise ValueError("proof too long")
        return leaf
    if not proof:
        raise ValueError("proof too short")
    k = _split(n)
    if index < k:
        return node_hash(root_from_proof(leaf, index, k, proof[:-1]), proof[-1])
    return node_hash(proof[-1], root_from_proof(leaf, index - k, n - k, proof[:-1]))


def verify_proof(leaf: bytes, index: int, n: int, proof: list, root: bytes) -> bool:
    try:
        return root_from_proof(leaf, index, n, proof) == root
    except ValueError:
        return False


def record_leaf(rid: bytes, aid: bytes, values: tuple) -> bytes:
    d, e, v, reward, reputation = values
    return leaf_hash(rid + aid + d + e + v + reward.to_bytes(4, "big")
                     + reputation.to_bytes(4, "big"))


def registration_leaf(aid: bytes, key: str, model_hash: bytes) -> bytes:
    return leaf_hash(aid + bytes.fromhex(key[2:]) + model_hash)


def anchor_label(name: str, index: int = 0) -> bytes:
    return sha256({"anchor": name, "index": index})


# --- contracts --------------------------------------------------------------------------

def compile_hardened() -> tuple[dict, dict]:
    return compile_contract(REGISTRY_V2), compile_contract(ANCHOR)


def _deploy(w3, compiled, sender):
    factory = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
    receipt = w3.eth.wait_for_transaction_receipt(
        factory.constructor().transact({"from": sender}), RECEIPT_TIMEOUT)
    return w3.eth.contract(address=receipt["contractAddress"], abi=compiled["abi"]), \
        receipt["gasUsed"]


def _transact(w3, call, sender):
    """(accepted, revert reason or None, receipt or None)."""
    from web3.exceptions import ContractLogicError
    try:
        tx = call.transact({"from": sender})
    except ContractLogicError as err:
        message = getattr(err, "message", None) or str(err)
        return False, message.split("execution reverted: ")[-1].split("'")[0].strip(), None
    receipt = w3.eth.wait_for_transaction_receipt(tx, RECEIPT_TIMEOUT)
    return receipt["status"] == 1, None, receipt


class HardenedLedger:
    """Client of one deployed ProvenanceRegistryV2."""

    def __init__(self, w3, compiled: dict):
        self.w3 = w3
        self.owner = w3.eth.accounts[0]
        self.contract, self.deploy_gas = _deploy(w3, compiled, self.owner)
        self.chain_id = w3.eth.chain_id
        self.address = self.contract.address

    def register(self, identities: list) -> int:
        gas = 0
        for ident in identities:
            ok, reason, receipt = _transact(self.w3, self.contract.functions.registerAgent(
                ident.id, ident.account.address, ident.model_hash), self.owner)
            if not ok:
                raise RuntimeError(f"registration refused: {reason}")
            gas += receipt["gasUsed"]
        return gas

    def registered(self, aid: bytes) -> tuple:
        key, model_hash = self.contract.functions.agents(aid).call()
        return key, bytes(model_hash)

    def entry(self, rid: bytes, ident: AgentIdentity, artifact: dict, *, signer=None,
              model_hash: bytes = None, signed_rid: bytes = None, signed_for=None,
              change_explanation: bool = False) -> tuple:
        """A record entry as the contract takes it. The keyword arguments build the attacks
        of A9.2: another signer, another model hash, a signature made for another record id
        or another (chain id, contract), or content changed after signing."""
        d, e, v, reward, rep = onchain_values(artifact)
        model_hash = ident.model_hash if model_hash is None else model_hash
        chain_id, contract = signed_for or (self.chain_id, self.address)
        sig = sign(signer or ident.account,
                   signed_digest(chain_id, contract, signed_rid or rid, ident.id, d, e, v,
                                 model_hash))
        if change_explanation:
            e = sha256({"changed after signing": e.hex()})
        return (rid, ident.id, d, e, v, model_hash, reward, rep, sig)

    def write(self, entries: list, batch_size: int = 100) -> list:
        import time
        txs = []
        for start in range(0, len(entries), batch_size):
            chunk = entries[start:start + batch_size]
            call = (self.contract.functions.record(chunk[0]) if batch_size == 1
                    else self.contract.functions.recordBatch(chunk))
            begin = time.perf_counter()
            ok, reason, receipt = _transact(self.w3, call, self.owner)
            seconds = time.perf_counter() - begin
            if not ok:
                raise RuntimeError(f"record transaction refused: {reason}")
            txs.append({"records": len(chunk), "gas": receipt["gasUsed"],
                        "seconds": seconds})
        return txs

    def try_write(self, entry: tuple, sender=None) -> tuple:
        ok, reason, _ = _transact(self.w3, self.contract.functions.record(entry),
                                  sender or self.owner)
        return ok, reason

    def fetch(self, rid: bytes):
        from web3.exceptions import ContractLogicError
        try:
            aid, d, e, v, reward, rep, _ = self.contract.functions.get(rid).call()
        except ContractLogicError:
            return None
        return bytes(aid), (bytes(d), bytes(e), bytes(v), reward, rep)

    def verify(self, rid: bytes, artifact: dict) -> str:
        stored = self.fetch(rid)
        if stored is None:
            return MISSING
        return VALID if stored[1] == onchain_values(artifact) else TAMPERED

    def leaf(self, rid: bytes) -> bytes:
        aid, values = self.fetch(rid)
        return record_leaf(rid, aid, values)


class AnchorChain:
    """Client of one deployed AnchorRegistry (on the second node)."""

    def __init__(self, w3, compiled: dict):
        self.w3 = w3
        self.owner = w3.eth.accounts[0]
        self.contract, self.deploy_gas = _deploy(w3, compiled, self.owner)

    def anchor(self, label: bytes, root: bytes, leaves: int) -> int:
        ok, reason, receipt = _transact(
            self.w3, self.contract.functions.anchor(label, root, leaves), self.owner)
        if not ok:
            raise RuntimeError(f"anchor refused: {reason}")
        return receipt["gasUsed"]

    def get(self, index: int) -> tuple:
        label, root, leaves, _ = self.contract.functions.get(index).call()
        return bytes(label), bytes(root), leaves

    def size(self) -> int:
        return self.contract.functions.size().call()


__all__ = ["MISSING", "TAMPERED", "VALID", "AgentIdentity", "AnchorChain", "HardenedLedger",
           "agent_id", "anchor_label", "compile_hardened", "merkle_proof", "merkle_root",
           "model_identity", "record_leaf", "registration_leaf", "root_from_proof",
           "signed_digest", "sign", "derived_account", "verify_proof", "leaf_hash", "node_hash"]
