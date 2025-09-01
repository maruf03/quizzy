"""Global context data for templates.

Keep values lightweight (counts, flags, simple strings). Avoid heavy queries.
"""

from __future__ import annotations

from django.conf import settings
from django.utils import timezone


def global_ui(request):
    """Provide global UI constants & lightweight per-user aggregates.

    Returned keys become template variables.
    """
    user = getattr(request, "user", None)
    pending_invites = 0
    active_attempts = 0
    if user and user.is_authenticated:
        try:
            from quizzes.models import Invitation
            from submissions.models import Submission
            pending_invites = Invitation.objects.filter(
                email=user.email, accepted__isnull=True
            ).count()
            active_attempts = Submission.objects.filter(user=user).count()
        except Exception:  # pragma: no cover - defensive, avoid total failure
            pass

    feature_flags = getattr(settings, "FEATURE_FLAGS", {})

    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Quizzy"),
        "APP_VERSION": getattr(settings, "APP_VERSION", "dev"),
        "ENV_LABEL": getattr(settings, "ENV_LABEL", ""),
        "DEFAULT_THEME": getattr(settings, "DEFAULT_THEME", "light"),
        "ENABLE_REALTIME": feature_flags.get("realtime", True),
        "FEATURE_FLAGS": feature_flags,
        "PENDING_INVITES_COUNT": pending_invites,
        "ACTIVE_QUIZ_ATTEMPTS": active_attempts,
        "MAX_QUIZ_ATTEMPTS": getattr(settings, "MAX_QUIZ_ATTEMPTS", 3),
        "BUILD_TIMESTAMP": getattr(settings, "BUILD_TIMESTAMP", None) or timezone.now(),
    }
