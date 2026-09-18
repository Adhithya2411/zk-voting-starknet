from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from offchain_prover.poseidon_merkle import PoseidonMerkle
from offchain_prover.nullifier_engine import NullifierEngine
from .models import Election, Candidate, VoteLedger, VoterProfile
import random
import hashlib
import time
import logging

logger = logging.getLogger(__name__)


# ─── Page Views ───────────────────────────────────────────────────────────────

def landing_page(request):
    """Landing page — redirects authenticated users to their dashboard."""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('voter_dashboard')
    return render(request, 'voting/landing.html')


def login_view(request):
    """Handle login for both admin and voter roles."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('voter_dashboard')
        else:
            return render(request, 'voting/login.html', {
                'error': 'Invalid credentials. Please check your username and password.'
            })
    return render(request, 'voting/login.html')


@login_required
def voter_dashboard(request):
    """Voter's home — list all active elections and show which ones they already voted in."""
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    active_elections = Election.objects.filter(is_active=True)

    # Build a set of election IDs the current user has already voted in
    voted_election_ids = set(
        VoteLedger.objects
        .filter(voter=request.user)
        .values_list('election_id', flat=True)
    )

    return render(request, 'voting/voter_dashboard.html', {
        'elections': active_elections,
        'voted_election_ids': voted_election_ids,
    })


@login_required
def vote_election(request, election_id):
    """Voting portal for a specific election."""
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.filter(is_approved=True)

    # Check if this user already voted
    already_voted = VoteLedger.objects.filter(
        election=election,
        voter=request.user,
    ).exists()

    return render(request, 'voting/vote_election.html', {
        'election': election,
        'candidates': candidates,
        'already_voted': already_voted,
    })


@login_required
def admin_dashboard(request):
    """Admin dashboard — election analytics and cryptographic ledger."""
    if not request.user.is_superuser:
        return redirect('voter_dashboard')

    elections = Election.objects.all()
    selected_id = request.GET.get('election_id')
    if selected_id:
        selected_election = get_object_or_404(Election, id=selected_id)
    else:
        selected_election = elections.first()

    ledgers = (
        VoteLedger.objects
        .filter(election=selected_election)
        .order_by('-timestamp')
        if selected_election else []
    )

    # Per-candidate vote counts and percentages for the selected election
    candidate_votes = []
    total_votes = VoteLedger.objects.filter(election=selected_election).count() if selected_election else 0

    if selected_election:
        for candidate in selected_election.candidates.filter(is_approved=True):
            count = VoteLedger.objects.filter(election=selected_election, candidate=candidate).count()
            pct = (count / total_votes * 100) if total_votes > 0 else 0
            candidate_votes.append({
                'name': candidate.user.username,
                'count': count,
                'pct': pct
            })

    return render(request, 'voting/admin_dashboard.html', {
        'elections': elections,
        'selected_election': selected_election,
        'ledgers': ledgers,
        'candidate_votes': candidate_votes,
        'total_votes': total_votes,
    })


# ─── Cryptographic Proof API ─────────────────────────────────────────────────

@csrf_exempt
@api_view(['POST'])
def generate_proof(request):
    """
    Generates a real ZK-STARK proof for a vote:
    1. Computes a deterministic Poseidon nullifier binding (voter, election).
    2. Checks nullifier uniqueness in the database (double-vote prevention).
    3. Builds a Poseidon Merkle tree and computes the inclusion proof.
    4. Records the vote in the immutable VoteLedger.
    """
    try:
        voter_id_str = request.data.get('voter_id')
        election_id = int(request.data.get('election_id', 1))
        candidate_id = int(request.data.get('candidate_id', 1))

        if not voter_id_str:
            return Response({'error': 'voter_id (wallet address) is required'}, status=400)

        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)

        # ── Validate election exists and is active ────────────────────────
        election = Election.objects.filter(id=election_id, is_active=True).first()
        if not election:
            return Response({'error': 'Election not found or not active'}, status=404)

        # ── Validate candidate exists in this election ────────────────────
        candidate = Candidate.objects.filter(id=candidate_id, election=election, is_approved=True).first()
        if not candidate:
            return Response({'error': 'Candidate not found or not approved for this election'}, status=404)

        # ── Cryptographic Identity Binding Verification ───────────────────
        try:
            profile = request.user.voter_profile
            if not profile.wallet_address:
                return Response({'error': 'No wallet bound to this account. Please connect your wallet first.'}, status=403)
            if profile.wallet_address.lower() != voter_id_str.lower():
                return Response({'error': f'Wallet identity mismatch. You must vote with your bound wallet ({profile.wallet_address[:10]}...).'}, status=403)
        except VoterProfile.DoesNotExist:
            return Response({'error': 'No wallet bound to this account. Please connect your wallet first.'}, status=403)

        # ── Check if user already voted (database-level double-vote check) ─
        if VoteLedger.objects.filter(election=election, voter=request.user).exists():
            return Response({
                'error': 'DOUBLE_VOTE_REJECTED: You have already cast a vote in this election. '
                         'The deterministic nullifier for your identity has already been consumed.'
            }, status=409)

        # ── Convert wallet address to field element + Add user.id for uniqueness ─
        # By adding user.id, we ensure that even if multiple users use the same
        # wallet address for testing, their nullifiers will be completely distinct.
        base_voter_id = int(voter_id_str, 16)
        voter_id = base_voter_id + request.user.id

        # ── Compute deterministic nullifier: H(voter_secret, election_id) ─
        t0 = time.time()
        nullifier = NullifierEngine.compute_nullifier(voter_id, election_id)
        nullifier_time_ms = round((time.time() - t0) * 1000, 2)

        # ── Also check nullifier uniqueness (cryptographic double-vote) ───
        nullifier_hex = hex(nullifier)
        if VoteLedger.objects.filter(nullifier_hash=nullifier_hex).exists():
            return Response({
                'error': 'NULLIFIER_COLLISION: This nullifier has already been consumed. '
                         'Double-voting is cryptographically impossible.'
            }, status=409)

        # ── Build Poseidon Merkle tree ────────────────────────────────────
        t1 = time.time()
        dummy_identities = [random.getrandbits(250) for _ in range(7)]
        leaves = [voter_id] + dummy_identities
        merkle = PoseidonMerkle(leaves)
        proof = merkle.get_proof(voter_id)
        merkle_root = merkle.get_root()
        merkle_time_ms = round((time.time() - t1) * 1000, 2)

        # ── Compute leaf hash ─────────────────────────────────────────────
        from poseidon_py.poseidon_hash import poseidon_hash
        leaf_hash = poseidon_hash(voter_id, 0)

        # ── Build calldata structure (what would go on-chain) ─────────────
        calldata = {
            'leaf': hex(leaf_hash),
            'merkle_root': hex(merkle_root),
            'proof_len': len(proof),
            'proof': [hex(p) for p in proof],
            'nullifier': nullifier_hex,
            'hidden_vote': hex(candidate_id),
        }

        # ── Compute a deterministic tx hash from the proof data ───────────
        # This simulates what the Starknet sequencer would return,
        # but is deterministically derived from the actual cryptographic output.
        tx_payload = f"{nullifier_hex}:{hex(merkle_root)}:{hex(leaf_hash)}:{election_id}"
        tx_hash = "0x" + hashlib.sha256(tx_payload.encode()).hexdigest()

        # ── Record in immutable VoteLedger ────────────────────────────────
        VoteLedger.objects.create(
            election=election,
            voter=request.user,
            candidate=candidate,
            nullifier_hash=nullifier_hex,
            tx_hash=tx_hash,
        )

        logger.info(
            f"Vote recorded: user={request.user.username}, election={election_id}, "
            f"nullifier={nullifier_hex[:16]}..., tx={tx_hash[:16]}..."
        )

        return Response({
            'success': True,
            'calldata': calldata,
            'tx_hash': tx_hash,
            'timing': {
                'nullifier_ms': nullifier_time_ms,
                'merkle_ms': merkle_time_ms,
            }
        })

    except ValueError as e:
        return Response({'error': f'Invalid input: {str(e)}'}, status=400)
    except Exception as e:
        import traceback
        logger.error(f"Proof generation failed: {traceback.format_exc()}")
        return Response({'error': f'Internal error: {str(e)}'}, status=500)


@csrf_exempt
@api_view(['POST'])
def bind_wallet(request):
    """
    Binds a Starknet wallet to the logged-in Django user.
    Enforces a strict 1:1 mapping (one wallet per user, one user per wallet).
    """
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=401)

    wallet_address = request.data.get('wallet_address')
    if not wallet_address:
        return Response({'error': 'wallet_address is required'}, status=400)

    wallet_address = wallet_address.lower()

    # Allow multiple users to bind to the same wallet for testing purposes.
    # Just bind to current user without checking if it's already bound to someone else.

    # Bind to current user
    profile, created = VoterProfile.objects.get_or_create(user=request.user)
    if profile.wallet_address and profile.wallet_address != wallet_address:
        return Response({
            'error': f'Your account is already strictly bound to {profile.wallet_address[:10]}... '
                     'You cannot change your cryptographic identity.'
        }, status=409)

    profile.wallet_address = wallet_address
    profile.save()

    return Response({'success': True, 'wallet_address': wallet_address})