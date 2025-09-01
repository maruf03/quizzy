from django.test import TestCase
from django.contrib.auth.models import User

from quizzes.models import Quiz, Question
from submissions.models import Submission, QuestionAttempt
from submissions.services import recompute_score


class ScoringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="x")
        self.quiz = Quiz.objects.create(title="Q1", creator=self.user, is_published=True)
        self.q1 = Question.objects.create(quiz=self.quiz, text="1+1?")
        self.sub = Submission.objects.create(quiz=self.quiz, user=self.user)

    def test_best_attempt(self):
        self.quiz.scoring_policy = "best"
        self.quiz.save(update_fields=["scoring_policy"])
        QuestionAttempt.objects.create(submission=self.sub, question=self.q1, is_correct=False, attempt_number=1)
        QuestionAttempt.objects.create(submission=self.sub, question=self.q1, is_correct=True, attempt_number=2)
        total = recompute_score(self.sub)
        self.assertEqual(total, 1)

    def test_first_attempt(self):
        self.quiz.scoring_policy = "first"
        self.quiz.save(update_fields=["scoring_policy"])
        QuestionAttempt.objects.create(submission=self.sub, question=self.q1, is_correct=True, attempt_number=1)
        QuestionAttempt.objects.create(submission=self.sub, question=self.q1, is_correct=False, attempt_number=2)
        total = recompute_score(self.sub)
        self.assertEqual(total, 1)

    def test_last_attempt(self):
        self.quiz.scoring_policy = "last"
        self.quiz.save(update_fields=["scoring_policy"])
        QuestionAttempt.objects.create(submission=self.sub, question=self.q1, is_correct=False, attempt_number=1)
        QuestionAttempt.objects.create(submission=self.sub, question=self.q1, is_correct=True, attempt_number=2)
        total = recompute_score(self.sub)
        self.assertEqual(total, 1)
