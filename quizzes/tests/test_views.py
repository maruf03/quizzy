from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from quizzes.models import Quiz, Question, Answer
from submissions.models import Submission


class QuizViewsTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="x")
        self.user = User.objects.create_user(username="u", password="x")
        self.quiz = Quiz.objects.create(title="Math", description="desc", creator=self.creator, is_published=True)
        self.q1 = Question.objects.create(quiz=self.quiz, text="1+1?")
        self.a1 = Answer.objects.create(question=self.q1, text="2", is_correct=True)
        self.a2 = Answer.objects.create(question=self.q1, text="3", is_correct=False)

    def test_quiz_list_public(self):
        url = reverse('quizzes:list')
        res = self.client.get(url)
        self.assertContains(res, self.quiz.title)

    def test_quiz_detail_published(self):
        url = reverse('quizzes:detail', args=[self.quiz.id])
        res = self.client.get(url)
        self.assertContains(res, self.quiz.title)

    def test_take_and_results_flow(self):
        self.client.login(username='u', password='x')
        take_url = reverse('quizzes:take', args=[self.quiz.id])
        # Render page
        res_get = self.client.get(take_url)
        self.assertEqual(res_get.status_code, 200)
        # Submit correct answer
        res_post = self.client.post(take_url, {f'answer_{self.q1.id}': str(self.a1.id)})
        self.assertEqual(res_post.status_code, 302)
        # Follow to results
        submission = Submission.objects.get(quiz=self.quiz, user=self.user)
        results_url = reverse('quizzes:results', args=[submission.id])
        res_results = self.client.get(results_url)
        self.assertContains(res_results, 'Score: 1')
