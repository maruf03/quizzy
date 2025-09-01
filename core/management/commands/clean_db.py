from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from quizzes.models import Quiz, Question, Answer, Invitation
from submissions.models import Submission, QuestionAttempt


class Command(BaseCommand):
    help = "Clean (purge) application data: quizzes, questions, answers, invitations, submissions, attempts, and (optionally) non-superuser accounts."

    def add_arguments(self, parser):
        parser.add_argument("--include-users", action="store_true", help="Also delete non-superuser user accounts.")
        parser.add_argument("--force", action="store_true", help="Skip interactive confirmation.")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without performing deletions.")

    def handle(self, *args, **options):
        include_users = options["include_users"]
        force = options["force"]
        dry_run = options["dry_run"]

        User = get_user_model()

        # Query counts up-front
        counts = {
            "quizzes": Quiz.objects.count(),
            "questions": Question.objects.count(),
            "answers": Answer.objects.count(),
            "invitations": Invitation.objects.count(),
            "submissions": Submission.objects.count(),
            "question_attempts": QuestionAttempt.objects.count(),
        }
        if include_users:
            counts["users_non_super"] = User.objects.filter(is_superuser=False).count()

        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN] Nothing will be deleted."))
            for k, v in counts.items():
                self.stdout.write(f"{k}: {v}")
            return

        if not force:
            self.stdout.write("You are about to permanently delete:")
            for k, v in counts.items():
                self.stdout.write(f"  - {k}: {v}")
            if include_users:
                self.stdout.write(self.style.WARNING("Including ALL non-superuser accounts"))
            confirm = input("Type 'yes' to continue: ").strip().lower()
            if confirm != "yes":
                raise CommandError("Aborted.")

        with transaction.atomic():
            # Delete in dependency-safe order
            QuestionAttempt.objects.all().delete()
            Submission.objects.all().delete()
            Invitation.objects.all().delete()
            Answer.objects.all().delete()
            Question.objects.all().delete()
            Quiz.objects.all().delete()
            deleted_users = 0
            if include_users:
                deleted_users, _ = User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Database cleaned."))
        for k, v in counts.items():
            self.stdout.write(f"Removed {k}: {v}")
        if include_users:
            self.stdout.write(f"Removed non-superuser user rows: {deleted_users}")
        self.stdout.write("You can now reseed with: python manage.py seed_demo --fresh")
