import logging
from typing import List
from poseidon_py.poseidon_hash import poseidon_hash

# Configure logging for off-chain prover execution
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class PoseidonMerkleTree:
    """
    Cryptographic Merkle Tree using Starknet's native Poseidon hash.
    Generates the state root and zero-knowledge inclusion proofs for the Cairo contract.
    """
    def __init__(self, leaves: List[int]):
        if not leaves:
            raise ValueError("Cannot initialize tree with empty leaves")
        
        # Hash raw voter IDs to form the base layer (leaves) of the tree
        self.leaves = [poseidon_hash(leaf, 0) for leaf in leaves]
        self.tree = self._build_tree(self.leaves)

    def _build_tree(self, current_level: List[int]) -> List[List[int]]:
        """
        Recursively computes parent nodes up to the state root.
        Enforces Cairo 2.x numerical sorting for deterministic hashing.
        """
        tree = [current_level]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # Handle odd-numbered levels by duplicating the last node
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Sort nodes (smaller first) to ensure position-agnostic verification on-chain
                node_min, node_max = min(left, right), max(left, right)
                next_level.append(poseidon_hash(node_min, node_max))
            
            tree.append(next_level)
            current_level = next_level
        
        return tree

    def get_root(self) -> int:
        """Retrieves the Merkle Root for contract state initialization."""
        return self.tree[-1][0]

    def get_proof(self, raw_voter_id: int) -> List[int]:
        """
        Computes the sibling path (ZK proof) required to verify a voter's inclusion.
        """
        target_hash = poseidon_hash(raw_voter_id, 0)
        if target_hash not in self.leaves:
            raise ValueError("Voter ID not found in current state")
        
        index = self.leaves.index(target_hash)
        proof = []
        
        for level in self.tree[:-1]:
            is_right_node = index % 2 == 1
            sibling_index = index - 1 if is_right_node else index + 1
            
            if sibling_index < len(level):
                proof.append(level[sibling_index])
            else:
                proof.append(level[index])
            
            index //= 2
            
        return proof

if __name__ == "__main__":
    # Initialize mock felt252 wallet addresses for terminal verification
    mock_voter_wallets = [
        int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16),
        int("0x03d22ce470c14b19642d51fb5dfd553b53cb1912f32777b7cb27a659ccab2136", 16),
        int("0x01a34382103f56ce43764b8cb6e0817c76b97da05ea7e3f89073c66f57007e60", 16)
    ]
    
    tree = PoseidonMerkleTree(mock_voter_wallets)
    logging.info(f"Merkle Root: {hex(tree.get_root())}")
    
    target_voter = mock_voter_wallets[1]
    proof = tree.get_proof(target_voter)
    
    logging.info("ZK Proof Path for Voter 2:")
    for idx, p in enumerate(proof):
        logging.info(f"  Level {idx}: {hex(p)}")