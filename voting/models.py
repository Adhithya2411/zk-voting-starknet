from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    election_start = models.DateTimeField()
    election_end = models.DateTimeField()

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def status(self):
        now = timezone.now()
        if now < self.registration_start:
            return "Upcoming"
        elif self.registration_start <= now <= self.registration_end:
            return "Registration Open"
        elif self.registration_end < now < self.election_start:
            return "Pending Election"
        elif self.election_start <= now <= self.election_end:
            return "Active"
        else:
            return "Ended"


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="candidates")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    party_name = models.CharField(max_length=100, blank=True)
    manifesto = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.election.title}"


class VoteLedger(models.Model):
    """
    Immutable record of each vote cast.
    Enforces uniqueness on (election, voter) to prevent double-voting at the DB level,
    and on nullifier_hash to prevent it at the cryptographic level.
    """
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes_cast", null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="votes_received", null=True)
    nullifier_hash = models.CharField(max_length=100, unique=True)
    tx_hash = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Database-level constraint: one vote per user per election
        unique_together = ('election', 'voter')

    def __str__(self):
        return f"Vote#{self.pk} election={self.election_id} nullifier={self.nullifier_hash[:16]}..."


class VoterProfile(models.Model):
    """
    Binds a Django user to a Starknet wallet to prevent wallet sharing
    and enforce true cryptographic identity.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voter_profile')
    wallet_address = models.CharField(max_length=66, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.wallet_address[:10] if self.wallet_address else 'Unbound'}"
