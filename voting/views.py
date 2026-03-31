import sys
import os
from django.http import JsonResponse
from django.shortcuts import render 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from offchain_prover.merkle_builder import PoseidonMerkleTree, NullifierGenerator, CalldataFormatter

def index(request):
    """Renders the main frontend voting interface."""
    return render(request, 'voting/index.html')

def generate_proof(request):
    try:
        target_wallet_hex = request.GET.get('wallet')
        if not target_wallet_hex:
            raise ValueError("No wallet address provided by frontend")

        target_voter = int(target_wallet_hex, 16)

        dummy_registered_voters = [
            int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16),
            int("0x03d22ce470c14b19642d51fb5dfd553b53cb1912f32777b7cb27a659ccab2136", 16),
            int("0x076764200e01cb36784b19c1fb26885fb6a6f893b8c8a6f716b3a94293b84357", 16) 
        ]

        if target_voter not in dummy_registered_voters:
            raise ValueError("Wallet is not registered in the Merkle Tree")

        tree = PoseidonMerkleTree(dummy_registered_voters)
        merkle_root = hex(tree.get_root())
        print(f"\n\n=== COPY THIS MERKLE ROOT ===\n{merkle_root}\n=============================\n")
        
        ELECTION_ID = 1

        proof_data = tree.get_proof(target_voter)
        hex_proof = [hex(p) for p in proof_data]

        nullifier = hex(NullifierGenerator.generate_nullifier(target_voter, ELECTION_ID))

        calldata = CalldataFormatter.format_vote_payload(int(nullifier, 16), proof_data)
        hex_calldata = [hex(x) for x in calldata]

        return JsonResponse({
            "status": "success",
            "wallet": target_wallet_hex,
            "election_id": ELECTION_ID,
            "merkle_root": merkle_root,
            "leaf": target_wallet_hex,
            "proof": hex_proof,
            "nullifier": nullifier,
            "cairo_calldata": hex_calldata
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)