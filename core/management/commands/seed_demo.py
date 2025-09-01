from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from random import random

from quizzes.models import Quiz, Question, Answer, Invitation
from submissions.models import Submission, QuestionAttempt


class Command(BaseCommand):
    help = "Seed the database with demo users, quizzes, questions, answers, invitations, and submissions."

    def add_arguments(self, parser):
        parser.add_argument("--fresh", action="store_true", help="Clear existing demo data before seeding")

    def handle(self, *args, **options):
        fresh = options.get("fresh")
        User = get_user_model()

        if fresh:
            self.stdout.write(self.style.WARNING("Clearing existing demo data..."))
            User.objects.filter(username__in=["creator", "invited", "tester1", "tester2", "tester3"]).delete()
            Quiz.objects.filter(title__startswith="Demo:").delete()

        with transaction.atomic():
            # Users
            creator, created_c = User.objects.get_or_create(username="creator", defaults={"email": "creator@example.com"})
            invited, created_i = User.objects.get_or_create(username="invited", defaults={"email": "invited@example.com"})
            tester1, created_1 = User.objects.get_or_create(username="tester1", defaults={"email": "tester1@example.com"})
            tester2, created_2 = User.objects.get_or_create(username="tester2", defaults={"email": "tester2@example.com"})
            tester3, created_3 = User.objects.get_or_create(username="tester3", defaults={"email": "tester3@example.com"})

            demo_users = [
                (creator, created_c),
                (invited, created_i),
                (tester1, created_1),
                (tester2, created_2),
                (tester3, created_3),
            ]

            for u, was_created in demo_users:
                # When a user is created without specifying password, Django stores '' which counts as usable.
                # Force-set a known password if newly created OR password field is blank/short.
                if was_created or not u.password or len(u.password) < 20:  # heuristic: real hashes are long
                    u.set_password("password123")
                    u.save(update_fields=["password"])

            # Quizzes
            public_quiz, _ = Quiz.objects.get_or_create(
                title="Demo: Public Quiz",
                defaults={
                    "description": "A sample public quiz",
                    "creator": creator,
                    "is_published": True,
                    "visibility": Quiz.PUBLIC,
                    "allow_multiple_attempts": False,
                    "scoring_policy": "best",
                },
            )
            private_quiz, _ = Quiz.objects.get_or_create(
                title="Demo: Private Quiz",
                defaults={
                    "description": "A sample private quiz",
                    "creator": creator,
                    "is_published": True,
                    "visibility": Quiz.PRIVATE,
                    "allow_multiple_attempts": True,
                    "max_attempts": 3,
                    "scoring_policy": "last",
                },
            )

            def ensure_questions(quiz: Quiz):
                if quiz.questions.exists():
                    return
                for i in range(1, 4):
                    q = Question.objects.create(quiz=quiz, text=f"Question {i}?")
                    correct_index = 1
                    for j in range(1, 4):
                        Answer.objects.create(
                            question=q,
                            text=f"Option {j}",
                            is_correct=(j == correct_index),
                        )

            ensure_questions(public_quiz)
            ensure_questions(private_quiz)

            # Invitations for private
            Invitation.objects.get_or_create(quiz=private_quiz, email=invited.email, defaults={"invited_by": creator, "accepted": True})

            # Submissions with varied scores
            def simulate_attempts(user, quiz):
                submission, _ = Submission.objects.get_or_create(quiz=quiz, user=user, attempt_number=1, defaults={"in_progress": True})
                for q in quiz.questions.all():
                    answers = list(q.answers.all())
                    chosen = None
                    if random() < 0.7:
                        chosen = next(a for a in answers if a.is_correct)
                    else:
                        chosen = next(a for a in answers if not a.is_correct)
                    QuestionAttempt.objects.create(
                        submission=submission,
                        question=q,
                        selected_answer_id=chosen.id,
                        is_correct=chosen.is_correct,
                        attempt_number=1,
                    )
                Submission.objects.filter(pk=submission.pk).update(in_progress=False)

            simulate_attempts(tester1, public_quiz)
            simulate_attempts(tester2, public_quiz)
            simulate_attempts(invited, private_quiz)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write("Login credentials: username 'creator' / 'invited' / 'tester1' etc., password 'password123'")
