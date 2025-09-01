from django.test import TestCase
from django.contrib.auth.models import User

from quizzes.models import Quiz
from submissions.models import Submission
from submissions.services import remaining_attempts


class RemainingAttemptsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="x")
        self.user = User.objects.create_user(username="u", password="x")
        self.quiz_single = Quiz.objects.create(title="Single", creator=self.owner, allow_multiple_attempts=False)
        self.quiz_multi = Quiz.objects.create(title="Multi", creator=self.owner, allow_multiple_attempts=True, max_attempts=2)

    def test_single_attempt_allowed_once(self):
        self.assertEqual(remaining_attempts(self.user, self.quiz_single.id), 1)
        Submission.objects.create(quiz=self.quiz_single, user=self.user)
        self.assertEqual(remaining_attempts(self.user, self.quiz_single.id), 0)

    def test_multi_with_max(self):
        self.assertEqual(remaining_attempts(self.user, self.quiz_multi.id), 2)
        Submission.objects.create(quiz=self.quiz_multi, user=self.user, attempt_number=1)
        self.assertEqual(remaining_attempts(self.user, self.quiz_multi.id), 1)
        Submission.objects.create(quiz=self.quiz_multi, user=self.user, attempt_number=2)
        self.assertEqual(remaining_attempts(self.user, self.quiz_multi.id), 0)
