from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


class EmailOrUsernameBackend:
    """Authenticate using either username or email and a password."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        user = User.objects.filter(Q(username=username) | Q(email=username)).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id).first()
