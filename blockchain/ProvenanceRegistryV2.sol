// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

/// Hardened provenance registry (protocol amendment 9). As ProvenanceRegistry, plus:
/// - model registration: each agent id is bound once to a signing key and a model hash;
/// - agent signatures: a record is accepted only if the agent's registered key signed its
///   record id, agent id, artifact hashes and model hash for this chain and this contract.
/// Reward and reputation are computed by the mechanism and are written by the owner.
/// A record still proves integrity, not truth.
contract ProvenanceRegistryV2 {
    struct Agent {
        address key;
        bytes32 modelHash;
    }

    struct Record {
        bytes32 agentId;
        bytes32 decisionHash;
        bytes32 explanationHash;
        bytes32 evidenceHash;
        uint32 reward;      // reward x 1e6
        uint32 reputation;  // reputation x 1e6
        uint64 timestamp;   // block timestamp when recorded
    }

    struct Entry {
        bytes32 recordId;
        bytes32 agentId;
        bytes32 decisionHash;
        bytes32 explanationHash;
        bytes32 evidenceHash;
        bytes32 modelHash;
        uint32 reward;
        uint32 reputation;
        bytes signature;    // 65 bytes: r, s, v
    }

    // upper bound of s for a canonical (low-s) secp256k1 signature
    uint256 private constant HALF_N =
        0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0;

    address public immutable owner;
    mapping(bytes32 => Agent) public agents;
    mapping(bytes32 => Record) private records;
    uint256 public count;

    event AgentRegistered(bytes32 indexed agentId, address key, bytes32 modelHash);
    event Recorded(bytes32 indexed recordId, bytes32 indexed agentId, bytes32 decisionHash,
                   bytes32 explanationHash, bytes32 evidenceHash, uint32 reward,
                   uint32 reputation);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    function registerAgent(bytes32 agentId, address key, bytes32 modelHash) external onlyOwner {
        require(key != address(0), "zero key");
        require(agents[agentId].key == address(0), "agent exists");
        agents[agentId] = Agent(key, modelHash);
        emit AgentRegistered(agentId, key, modelHash);
    }

    /// The 32-byte message an agent signs (before the EIP-191 prefix).
    function digest(bytes32 recordId, bytes32 agentId, bytes32 decisionHash,
                    bytes32 explanationHash, bytes32 evidenceHash, bytes32 modelHash)
        public view returns (bytes32)
    {
        return keccak256(abi.encode(block.chainid, address(this), recordId, agentId,
                                    decisionHash, explanationHash, evidenceHash, modelHash));
    }

    function _signer(bytes32 message, bytes calldata sig) private pure returns (address) {
        require(sig.length == 65, "bad signature length");
        bytes32 r = bytes32(sig[0:32]);
        bytes32 s = bytes32(sig[32:64]);
        uint8 v = uint8(sig[64]);
        require(uint256(s) <= HALF_N, "high s");
        require(v == 27 || v == 28, "bad v");
        bytes32 prefixed = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32",
                                                      message));
        return ecrecover(prefixed, v, r, s);
    }

    function _store(Entry calldata e) private {
        Agent memory agent = agents[e.agentId];
        require(agent.key != address(0), "agent not registered");
        require(e.modelHash == agent.modelHash, "model mismatch");
        bytes32 message = digest(e.recordId, e.agentId, e.decisionHash, e.explanationHash,
                                 e.evidenceHash, e.modelHash);
        require(_signer(message, e.signature) == agent.key, "bad signature");
        require(records[e.recordId].timestamp == 0, "record exists");
        records[e.recordId] = Record(e.agentId, e.decisionHash, e.explanationHash,
                                     e.evidenceHash, e.reward, e.reputation,
                                     uint64(block.timestamp));
        count += 1;
        emit Recorded(e.recordId, e.agentId, e.decisionHash, e.explanationHash,
                      e.evidenceHash, e.reward, e.reputation);
    }

    function record(Entry calldata entry) external onlyOwner {
        _store(entry);
    }

    function recordBatch(Entry[] calldata entries) external onlyOwner {
        for (uint256 i = 0; i < entries.length; i++) {
            _store(entries[i]);
        }
    }

    function get(bytes32 recordId) external view returns (Record memory) {
        require(records[recordId].timestamp != 0, "no record");
        return records[recordId];
    }
}
