from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth import authenticate


User = get_user_model()


class AuthBackendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="pass1234",
        )

    def test_login_with_username(self):
        user = authenticate(username="alice", password="pass1234")
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_login_with_email(self):
        user = authenticate(username="alice@example.com", password="pass1234")
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_login_invalid(self):
        user = authenticate(username="alice", password="wrong")
        self.assertIsNone(user)
