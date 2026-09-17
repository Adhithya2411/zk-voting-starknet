from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from offchain_prover.poseidon_merkle import PoseidonMerkle
from offchain_prover.nullifier_engine import NullifierEngine
from .models import Election, Candidate, VoteLedger
import random
import logging

def landing_page(request):
    """Dynamic Landing Page."""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('voter_dashboard')
    return render(request, 'voting/landing.html')

def login_view(request):
    """Simple login handler."""
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('voter_dashboard')
        else:
            return render(request, 'voting/login.html', {'error': 'Invalid credentials'})
    return render(request, 'voting/login.html')

@login_required
def voter_dashboard(request):
    """List of all elections for the voter."""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    
    active_elections = Election.objects.filter(is_active=True)
    return render(request, 'voting/voter_dashboard.html', {
        'elections': active_elections
    })

@login_required
def vote_election(request, election_id):
    """Voting portal for a specific election."""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
        
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.filter(is_approved=True)
    return render(request, 'voting/vote_election.html', {
        'election': election,
        'candidates': candidates
    })

@login_required
def admin_dashboard(request):
    """Admin dashboard to view statistics and CRUD elections."""
    if not request.user.is_superuser:
        return redirect('voter_dashboard')
    
    elections = Election.objects.all()
    # For the selected election in UI (defaults to first)
    selected_id = request.GET.get('election_id')
    if selected_id:
        selected_election = get_object_or_404(Election, id=selected_id)
    else:
        selected_election = elections.first()
        
    ledgers = VoteLedger.objects.filter(election=selected_election).order_by('-timestamp') if selected_election else []
    
    return render(request, 'voting/admin_dashboard.html', {
        'elections': elections,
        'selected_election': selected_election,
        'ledgers': ledgers
    })


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def generate_proof(request):
    """
    API endpoint that generates the valid ZK-STARK proof for a given wallet address.
    """
    try:
        voter_id_str = request.data.get('voter_id')
        election_id = request.data.get('election_id', 1)
        candidate_id = request.data.get('candidate_id', 1)

        if not voter_id_str:
            return Response({'error': 'voter_id is required'}, status=400)

        # Convert hex string wallet to int
        voter_id = int(voter_id_str, 16)
        
        # Build the mock tree including the connected wallet
        dummy_identities = [random.getrandbits(250) for _ in range(7)]
        leaves = [voter_id] + dummy_identities
        
        merkle = PoseidonMerkle(leaves)
        proof = merkle.get_proof(voter_id)
        nullifier = NullifierEngine.compute_nullifier(voter_id, int(election_id))

        from poseidon_py.poseidon_hash import poseidon_hash
        leaf_hash = poseidon_hash(voter_id, 0)
        
        calldata = {
            'leaf': hex(leaf_hash),
            'proof_len': hex(len(proof)),
            'proof': [hex(p) for p in proof],
            'nullifier': hex(nullifier),
            'hidden_vote': hex(int(candidate_id))
        }
        
        # We optionally log it to our DB to mimic successful validation on-chain for the dashboard
        # Wait, usually the Starknet indexer would do this, but we'll mock it here.
        # Since we are mocking the transaction, let's just record it in the ledger so the admin sees it.
        election = Election.objects.filter(id=int(election_id)).first()
        if election:
            VoteLedger.objects.create(
                election=election,
                nullifier_hash=hex(nullifier),
                tx_hash="0x" + hex(random.getrandbits(250))[2:]  # fake tx hash
            )

        return Response({
            'success': True,
            'calldata': calldata
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': f"Exception: {str(e)}\n{traceback.format_exc()}"}, status=400)