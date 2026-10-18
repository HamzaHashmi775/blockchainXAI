// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

/// Append-only registry of provenance records for agent decisions, explanations and evidence.
/// Only identifiers, SHA-256 hashes and two scaled numbers are stored; the artifacts
/// themselves stay off-chain. A record proves that an artifact has not changed since it was
/// recorded; it says nothing about whether the artifact is true.
contract ProvenanceRegistry {
    struct Record {
        bytes32 decisionHash;
        bytes32 explanationHash;
        bytes32 evidenceHash;
        uint32 reward;      // reward x 1e6
        uint32 reputation;  // reputation x 1e6
        uint64 timestamp;   // block timestamp when recorded
    }

    address public immutable owner;
    mapping(bytes32 => Record) private records;
    uint256 public count;

    event Recorded(bytes32 indexed recordId, bytes32 decisionHash, bytes32 explanationHash,
                   bytes32 evidenceHash, uint32 reward, uint32 reputation);

    constructor() {
        owner = msg.sender;
    }

    function _store(bytes32 recordId, bytes32 d, bytes32 e, bytes32 v, uint32 r, uint32 rep)
        private
    {
        require(records[recordId].timestamp == 0, "record exists");
        records[recordId] = Record(d, e, v, r, rep, uint64(block.timestamp));
        count += 1;
        emit Recorded(recordId, d, e, v, r, rep);
    }

    function record(bytes32 recordId, bytes32 decisionHash, bytes32 explanationHash,
                    bytes32 evidenceHash, uint32 reward, uint32 reputation) external {
        require(msg.sender == owner, "not owner");
        _store(recordId, decisionHash, explanationHash, evidenceHash, reward, reputation);
    }

    function recordBatch(bytes32[] calldata recordIds, bytes32[] calldata decisionHashes,
                         bytes32[] calldata explanationHashes, bytes32[] calldata evidenceHashes,
                         uint32[] calldata rewards, uint32[] calldata reputations) external {
        require(msg.sender == owner, "not owner");
        uint256 n = recordIds.length;
        require(decisionHashes.length == n && explanationHashes.length == n
                && evidenceHashes.length == n && rewards.length == n
                && reputations.length == n, "length mismatch");
        for (uint256 i = 0; i < n; i++) {
            _store(recordIds[i], decisionHashes[i], explanationHashes[i], evidenceHashes[i],
                   rewards[i], reputations[i]);
        }
    }

    function get(bytes32 recordId) external view returns (Record memory) {
        require(records[recordId].timestamp != 0, "no record");
        return records[recordId];
    }
}
