import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from voting.models import Election, Candidate, VoteLedger, VoterProfile
from offchain_prover.nullifier_engine import NullifierEngine
from offchain_prover.poseidon_merkle import PoseidonMerkle

class CryptoEngineTests(TestCase):
    def test_nullifier_determinism(self):
        """Test that the same input yields the same nullifier hash."""
        wallet = 0x1234567890abcdef
        election_id = 1
        hash1 = NullifierEngine.compute_nullifier(wallet, election_id)
        hash2 = NullifierEngine.compute_nullifier(wallet, election_id)
        self.assertEqual(hash1, hash2)
        
    def test_nullifier_uniqueness(self):
        """Test that different inputs yield different nullifier hashes."""
        hash1 = NullifierEngine.compute_nullifier(0xABC, 1)
        hash2 = NullifierEngine.compute_nullifier(0xDEF, 1)
        self.assertNotEqual(hash1, hash2)

    def test_merkle_tree_proof(self):
        """Test Merkle root generation and proof verification."""
        leaves = [123, 456, 789]
        tree = PoseidonMerkle(leaves)
        root = tree.get_root()
        self.assertIsNotNone(root)
        
        proof = tree.get_proof(456)
        self.assertGreater(len(proof), 0)

class VotingAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        
        self.election = Election.objects.create(
            title="Test Election",
            description="Test",
            registration_start="2020-01-01T00:00:00Z",
            registration_end="2020-01-02T00:00:00Z",
            election_start="2020-01-03T00:00:00Z",
            election_end="2099-01-04T00:00:00Z",
            is_active=True
        )
        self.candidate_user = User.objects.create_user(username="candidate1")
        self.candidate = Candidate.objects.create(
            election=self.election,
            user=self.candidate_user,
            is_approved=True
        )

    def test_wallet_binding(self):
        response = self.client.post(
            reverse('bind_wallet'),
            data=json.dumps({"wallet_address": "0xABCDEF123456"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(VoterProfile.objects.filter(user=self.user).exists())
        
    def test_generate_proof_and_vote(self):
        VoterProfile.objects.create(user=self.user, wallet_address="0x123456ABCDEF")
        
        payload = {
            "voter_id": "0x123456ABCDEF",
            "election_id": self.election.id,
            "candidate_id": self.candidate.id
        }
        
        # First vote
        response1 = self.client.post(
            reverse('generate_proof'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response1.status_code, 200)
        
        # Second vote should be rejected (Double Vote Prevention)
        response2 = self.client.post(
            reverse('generate_proof'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response2.status_code, 409)
        self.assertIn("DOUBLE_VOTE_REJECTED", response2.json()['error'])
