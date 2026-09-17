from poseidon_py.poseidon_hash import poseidon_hash
from typing import List

class PoseidonMerkle:
    """
    Dedicated module for the Poseidon Merkle Tree construction.
    Split from the monolithic merkle_builder.py to adhere to the modular architecture.
    """
    def __init__(self, leaves: List[int]):
        if not leaves:
            raise ValueError("Leaves cannot be empty")
        self.leaves = [poseidon_hash(leaf, 0) for leaf in leaves]
        self.tree = self._build_tree(self.leaves)

    def _build_tree(self, current_level: List[int]) -> List[List[int]]:
        tree = [current_level]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Enforce Cairo min/max ordering
                node_min, node_max = min(left, right), max(left, right)
                next_level.append(poseidon_hash(node_min, node_max))
            
            tree.append(next_level)
            current_level = next_level
        
        return tree

    def get_root(self) -> int:
        return self.tree[-1][0]

    def get_proof(self, raw_voter_id: int) -> List[int]:
        target_hash = poseidon_hash(raw_voter_id, 0)
        if target_hash not in self.leaves:
            raise ValueError("Voter ID not in leaves")
            
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
