from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from quizzes.models import Quiz
from submissions.models import Submission


class AttemptGuardMiddlewareTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="x")
        self.user = User.objects.create_user(username="u", password="x")
        self.quiz = Quiz.objects.create(title="Q", creator=self.owner, is_published=True)

    def test_owner_blocked(self):
        self.client.login(username="owner", password="x")
        url = reverse("quiz-start", kwargs={"pk": self.quiz.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.assertIn(b"Owners cannot attempt", res.content)

    def test_no_attempts_left_blocked(self):
        self.client.login(username="u", password="x")
        Submission.objects.create(quiz=self.quiz, user=self.user, attempt_number=1)
        url = reverse("quiz-start", kwargs={"pk": self.quiz.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.assertIn(b"No attempts left", res.content)

    def test_allowed_can_start(self):
        self.client.login(username="u", password="x")
        url = reverse("quiz-start", kwargs={"pk": self.quiz.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Started quiz", res.content)
