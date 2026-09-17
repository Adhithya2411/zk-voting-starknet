from poseidon_py.poseidon_hash import poseidon_hash
import logging

class NullifierEngine:
    @staticmethod
    def compute_nullifier(voter_secret: int, election_id: int) -> int:
        """
        Computes the deterministic nullifier binding a voter to a specific election,
        preventing double-voting while maintaining anonymity.
        """
        return poseidon_hash(voter_secret, election_id)

    @staticmethod
    def batch_generate(voter_secrets: list[int], election_id: int) -> list[int]:
        """
        Generates a batch of nullifiers, ensuring collision resistance.
        """
        nullifiers = []
        for secret in voter_secrets:
            nullifiers.append(NullifierEngine.compute_nullifier(secret, election_id))
        
        # Verify collision resistance (pigeonhole principle shouldn't apply here for reasonable lists)
        if len(set(nullifiers)) != len(nullifiers):
            logging.warning("CRITICAL: Hash collision detected in nullifier generation!")
            
        return nullifiers
