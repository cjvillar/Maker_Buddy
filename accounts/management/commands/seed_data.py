from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from maker_projects.models import MakerProject, CheckPoint
import random


class Command(BaseCommand):
    help = "Seed or Delete test data: python manage.py seed_data <--delete>"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete", action="store_true", help="Delete all seeded users and projects"
        )

    def handle(self, *args, **kwargs):

        if kwargs["delete"]:
            User.objects.filter(username__startswith="user").delete()
            self.stdout.write(
                self.style.SUCCESS("Deleted all seeded users and projects")
            )
            return

        self.stdout.write("Seeding data...")

        users = []

        for i in range(5):
            username = f"user{i}"
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@example.com"}
            )

            if created:
                user.set_password("password123")
                user.save()

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "display_name": f"Maker {i}",
                    "bio": "Building cool stuff",
                },
            )

            users.append(user)

        for user in users:
            for j in range(3):
                project = MakerProject.objects.create(
                    owner=user,
                    title=f"{user.username}'s Project {j}",
                    description="A really cool project",
                )

                for k in range(random.randint(2, 5)):
                    CheckPoint.objects.create(
                        project=project,
                        title=f"Checkpoint {k}",
                        description="Make progress",
                        order=k,
                    )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
