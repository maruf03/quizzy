from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()

class ProfileAndAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", email="alice@example.com", password="pass12345")

    def test_navbar_auth_visibility(self):
        resp = self.client.get(reverse("home"))
        self.assertContains(resp, "Login")
        self.client.login(username="alice", password="pass12345")
        resp = self.client.get(reverse("home"))
        self.assertNotContains(resp, "Login")
        self.assertContains(resp, "My Quizzes")

    def test_profile_update(self):
        self.client.login(username="alice", password="pass12345")
        url = reverse("accounts:profile")
        resp = self.client.post(url, {"first_name": "Al", "last_name": "Ice"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Al")
        self.assertEqual(self.user.last_name, "Ice")

    def test_password_reset_flow_sends_email(self):
        resp = self.client.post(reverse("password_reset"), {"email": "alice@example.com"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset", mail.outbox[0].subject)

    def test_anonymous_profile_redirect(self):
        url = reverse("accounts:profile")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.headers.get("Location"))

    def test_password_change(self):
        self.client.login(username="alice", password="pass12345")
        url = reverse("password_change")
        resp = self.client.post(url, {
            "old_password": "pass12345",
            "new_password1": "Newpass123!",
            "new_password2": "Newpass123!",
        })
        self.assertEqual(resp.status_code, 302)
        # Can login with new password
        self.client.logout()
        self.assertTrue(self.client.login(username="alice", password="Newpass123!"))
