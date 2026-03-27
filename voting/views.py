import sys
import os
from django.http import JsonResponse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from offchain_prover.merkle_builder import PoseidonMerkleTree, NullifierGenerator, CalldataFormatter

def generate_proof(request):
    try:
        # TODO: These will eventually come from the database/frontend payload
        ELECTION_ID = 1
        dummy_registered_voters = [
            int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16),
            int("0x03d22ce470c14b19642d51fb5dfd553b53cb1912f32777b7cb27a659ccab2136", 16),
            int("0x01a34382103f56ce43764b8cb6e0817c76b97da05ea7e3f89073c66f57007e60", 16)
        ]

        target_wallet_hex = "0x03d22ce470c14b19642d51fb5dfd553b53cb1912f32777b7cb27a659ccab2136"
        target_voter = int(target_wallet_hex, 16)

        # 1. Initialize Tree
        tree = PoseidonMerkleTree(dummy_registered_voters)
        merkle_root = hex(tree.get_root())

        # 2. Get Proof
        proof_data = tree.get_proof(target_voter)
        hex_proof = [hex(p) for p in proof_data]

        # 3. Generate Nullifier
        nullifier = hex(NullifierGenerator.generate_nullifier(target_voter, ELECTION_ID))

        # 4. Format for Cairo
        calldata = CalldataFormatter.format_vote_payload(int(nullifier, 16), proof_data)
        hex_calldata = [hex(x) for x in calldata]

        return JsonResponse({
            "status": "success",
            "wallet": target_wallet_hex,
            "election_id": ELECTION_ID,
            "merkle_root": merkle_root,
            "zk_proof": hex_proof,
            "nullifier": nullifier,
            "cairo_calldata": hex_calldata
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)