from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from quizzes.models import Quiz, Invitation


class InvitationTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="x", email="creator@example.com")
        self.user = User.objects.create_user(username="u", password="x", email="u@example.com")
        self.quiz_private = Quiz.objects.create(title="Priv", creator=self.creator, is_published=True, visibility=Quiz.PRIVATE)

    def test_creator_can_invite(self):
        self.client.login(username='creator', password='x')
        url = reverse('quizzes:invite', args=[self.quiz_private.id])
        res = self.client.post(url, {"email": "u@example.com"})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Invitation.objects.filter(quiz=self.quiz_private, email='u@example.com').exists())

    def test_private_requires_invitation(self):
        self.client.login(username='u', password='x')
        detail_url = reverse('quizzes:detail', args=[self.quiz_private.id])
        take_url = reverse('quizzes:take', args=[self.quiz_private.id])
        # Detail allowed (published), but taking should be blocked until accepted
        res_d = self.client.get(detail_url)
        self.assertEqual(res_d.status_code, 200)
        res_t = self.client.get(take_url)
        self.assertEqual(res_t.status_code, 404)
        # Accept invite then allowed
        self.client.logout()
        self.client.login(username='creator', password='x')
        invite_url = reverse('quizzes:invite', args=[self.quiz_private.id])
        self.client.post(invite_url, {"email": "u@example.com"})
        self.client.logout()
        self.client.login(username='u', password='x')
        accept_url = reverse('quizzes:accept-invite', args=[self.quiz_private.id])
        res_a = self.client.post(accept_url)
        self.assertEqual(res_a.status_code, 302)
        res_t2 = self.client.get(take_url)
        self.assertEqual(res_t2.status_code, 200)
