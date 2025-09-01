from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from quizzes.models import Quiz, Question, Answer, Invitation
from submissions.models import Submission


class QuizApiTests(APITestCase):
	def setUp(self):
		self.creator = User.objects.create_user(username="creator", password="pass", email="creator@example.com")
		self.invited = User.objects.create_user(username="invited", password="pass", email="invited@example.com")
		self.other = User.objects.create_user(username="other", password="pass", email="other@example.com")

		self.public_quiz = Quiz.objects.create(title="Pub", description="", creator=self.creator, is_published=True)
		self.private_quiz = Quiz.objects.create(
			title="Priv",
			description="",
			creator=self.creator,
			is_published=True,
			visibility=Quiz.PRIVATE,
		)

		# Add one question with two answers to each quiz
		for quiz in (self.public_quiz, self.private_quiz):
			q = Question.objects.create(quiz=quiz, text="Q1")
			self.correct = Answer.objects.create(question=q, text="A1", is_correct=True)
			self.wrong = Answer.objects.create(question=q, text="A2", is_correct=False)

	def test_list_public_quizzes(self):
		url = reverse("api:quiz-list")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		ids = [q["id"] for q in resp.data]
		self.assertIn(self.public_quiz.id, ids)
		self.assertNotIn(self.private_quiz.id, ids)

	def test_private_quiz_detail_requires_invite_or_creator(self):
		url = reverse("api:quiz-detail", args=[self.private_quiz.id])
		# Anonymous denied
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
		# Invited accepted can view
		Invitation.objects.create(quiz=self.private_quiz, email=self.invited.email, invited_by=self.creator, accepted=True)
		self.client.login(username="invited", password="pass")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		# Creator can view
		self.client.logout()
		self.client.login(username="creator", password="pass")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

	def test_submit_creates_submission(self):
		# Invite the user to private quiz and accept
		Invitation.objects.create(quiz=self.private_quiz, email=self.invited.email, invited_by=self.creator, accepted=True)
		self.client.login(username="invited", password="pass")
		url = reverse("api:quiz-submit", args=[self.private_quiz.id])
		# Gather question -> correct answer mapping
		q = self.private_quiz.questions.first()
		payload = {"answers": {str(q.id): self.correct.id}}
		resp = self.client.post(url, payload, format="json")
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		sub_id = resp.data["id"]
		sub = Submission.objects.get(pk=sub_id)
		self.assertEqual(sub.user, self.invited)
		self.assertFalse(sub.in_progress)


class SubmissionApiTests(APITestCase):
	def setUp(self):
		self.u1 = User.objects.create_user(username="u1", password="pass", email="u1@example.com")
		self.u2 = User.objects.create_user(username="u2", password="pass", email="u2@example.com")
		self.creator = User.objects.create_user(username="c", password="pass", email="c@example.com")
		self.quiz = Quiz.objects.create(title="Pub", description="", creator=self.creator, is_published=True)
		Submission.objects.create(quiz=self.quiz, user=self.u1, attempt_number=1, in_progress=False)
		Submission.objects.create(quiz=self.quiz, user=self.u1, attempt_number=2, in_progress=False)
		Submission.objects.create(quiz=self.quiz, user=self.u2, attempt_number=1, in_progress=False)

	def test_list_own_submissions(self):
		self.client.login(username="u1", password="pass")
		url = reverse("api:submission-list")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(len(resp.data), 2)
		self.assertTrue(all(s["user"] == self.u1.id for s in resp.data))

	def test_cannot_view_others_submission(self):
		self.client.login(username="u1", password="pass")
		other_sub = Submission.objects.filter(user=self.u2).first()
		url = reverse("api:submission-detail", args=[other_sub.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
