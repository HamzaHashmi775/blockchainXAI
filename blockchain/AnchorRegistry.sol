// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

/// Append-only list of Merkle roots (protocol amendment 9). Deployed on a chain the operator
/// of the provenance registry cannot rewrite (simulated in the experiment by a second, local
/// node), it lets an auditor detect a rewritten history of that registry.
contract AnchorRegistry {
    struct Anchor {
        bytes32 label;
        bytes32 root;
        uint64 leaves;
        uint64 timestamp;
    }

    address public immutable owner;
    Anchor[] private anchors;

    event Anchored(uint256 indexed index, bytes32 label, bytes32 root, uint64 leaves);

    constructor() {
        owner = msg.sender;
    }

    function anchor(bytes32 label, bytes32 root, uint64 leaves) external {
        require(msg.sender == owner, "not owner");
        require(leaves > 0, "empty");
        anchors.push(Anchor(label, root, leaves, uint64(block.timestamp)));
        emit Anchored(anchors.length - 1, label, root, leaves);
    }

    function size() external view returns (uint256) {
        return anchors.length;
    }

    function get(uint256 index) external view returns (Anchor memory) {
        return anchors[index];
    }
}
