import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from voting.models import Election, Candidate, VoteLedger
import random

class Command(BaseCommand):
    help = 'Seeds the database with admin, users, elections, and candidates'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # 1. Create Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@zkvote.com', 'admin123')
            self.stdout.write("Created superuser: admin (pw: admin123)")

        # 2. Create 5 mock users
        users = []
        for i in range(1, 6):
            username = f'voter{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, f'{username}@zkvote.com', 'password123')
                users.append(user)
                self.stdout.write(f"Created voter: {username} (pw: password123)")
            else:
                users.append(User.objects.get(username=username))

        # 3. Create a Demo Election
        now = timezone.now()
        election, created = Election.objects.get_or_create(
            title="Q3 Governance DAO Election",
            defaults={
                'description': "Vote on the primary focus for Q4 development: Scaling vs Ecosystem Growth vs Treasury Enhancement.",
                'registration_start': now - datetime.timedelta(days=7),
                'registration_end': now - datetime.timedelta(days=2),
                'election_start': now - datetime.timedelta(days=1),
                'election_end': now + datetime.timedelta(days=3),
                'is_active': True
            }
        )
        if created:
            self.stdout.write("Created active election: Q3 Governance DAO Election")

        # 4. Add Candidates
        parties = ["Decentralization Party", "Rollup Coalition", "Treasury Hawks"]
        manifestos = [
            "Focuses on layer-2 scaling and privacy-preserving infrastructure for the public good.",
            "Advocates for massive execution scale using Cairo and validium data availability.",
            "Aims to heavily invest DAO funds into high-yield DeFi strategies."
        ]
        
        # Make the first 3 users candidates
        for i in range(3):
            Candidate.objects.get_or_create(
                election=election,
                user=users[i],
                defaults={
                    'party_name': parties[i],
                    'manifesto': manifestos[i],
                    'is_approved': True
                }
            )
        self.stdout.write("Registered 3 candidates for the election")

        # 5. Seed some mock Ledger entries
        for i in range(15):
            nullifier = hex(random.getrandbits(250))
            tx_hash = hex(random.getrandbits(250))
            VoteLedger.objects.get_or_create(
                election=election,
                nullifier_hash=nullifier,
                defaults={
                    'tx_hash': tx_hash
                }
            )
        self.stdout.write("Seeded 15 mock vote ledger entries")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
