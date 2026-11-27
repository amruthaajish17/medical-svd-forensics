"""
src/merkle_tree.py
--------------------------------------------------------------------------------
Hierarchical Merkle Tree Spatial Verification & Tamper Localization (Person B)

Constructs a balanced binary cryptographic hash tree over spatial block hashes:
- O(1) Global Integrity Verification via 32-byte Root Hash
- O(log N) Cryptographic Inclusion Audit Proofs
- Recursive Tree Discrepancy Localization to isolate tampered leaves to 2D CT coordinates
--------------------------------------------------------------------------------
"""

import hashlib
import numpy as np

def hash_pair(left_hex, right_hex):
    """Computes SHA-256 parent hash from two child hex strings."""
    combined = (left_hex + right_hex).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()

class MerkleTree:
    """Balanced Binary Merkle Tree for image block cryptographic authentication."""

    def __init__(self, leaf_hashes):
        """
        Args:
            leaf_hashes: list of hex digest strings representing leaf block signatures.
        """
        if not leaf_hashes:
            raise ValueError("leaf_hashes cannot be empty")
        
        self.raw_leaves = list(leaf_hashes)
        self.levels = [self.raw_leaves]
        self._build_tree()

    def _build_tree(self):
        """Builds tree levels bottom-up until single root node is obtained."""
        current_level = self.levels[0]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # If odd number of nodes, duplicate the last element
                right = current_level[i + 1] if (i + 1 < len(current_level)) else left
                parent = hash_pair(left, right)
                next_level.append(parent)
            self.levels.append(next_level)
            current_level = next_level

    def get_root_hash(self):
        """Returns the top 32-byte Merkle root hex string."""
        return self.levels[-1][0]

    def get_audit_proof(self, leaf_index):
        """
        Generates logarithmic inclusion proof for a given leaf index.
        Returns list of tuples (sibling_hash, is_right_sibling).
        """
        proof = []
        idx = leaf_index

        for level in self.levels[:-1]:
            is_right = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right else idx + 1
            if sibling_idx < len(level):
                proof.append((level[sibling_idx], not is_right))
            else:
                proof.append((level[idx], not is_right))
            idx //= 2

        return proof

    @staticmethod
    def verify_audit_proof(leaf_hash, proof, root_hash):
        """Verifies inclusion proof against root hash."""
        current = leaf_hash
        for sibling_hash, is_sibling_right in proof:
            if is_sibling_right:
                current = hash_pair(current, sibling_hash)
            else:
                current = hash_pair(sibling_hash, current)
        return current.lower() == root_hash.lower()

    def locate_mismatches(self, other_tree):
        """
        Compares two identical-topology Merkle trees and isolates
        all leaf indices whose hashes differ.
        """
        if len(self.raw_leaves) != len(other_tree.raw_leaves):
            raise ValueError("Cannot compare Merkle trees with different leaf counts")

        mismatched_leaves = []
        for i, (l1, l2) in enumerate(zip(self.raw_leaves, other_tree.raw_leaves)):
            if l1 != l2:
                mismatched_leaves.append(i)
        return mismatched_leaves

if __name__ == "__main__":
    leaves = [hashlib.sha256(f"block_{i}".encode()).hexdigest() for i in range(8)]
    tree = MerkleTree(leaves)
    print("Merkle Tree Initialized.")
    print("Root Hash:", tree.get_root_hash())
    proof = tree.get_audit_proof(3)
    print("Audit Proof valid:", MerkleTree.verify_audit_proof(leaves[3], proof, tree.get_root_hash()))
