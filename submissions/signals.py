from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import QuestionAttempt
from .services import recompute_score
try:
    from realtime.utils import invalidate_leaderboard
except Exception:
    def invalidate_leaderboard(quiz_id: int):
        return None

try:
    from core.channels import broadcast_leaderboard
except Exception:  # pragma: no cover - placeholder if not yet implemented
    def broadcast_leaderboard(quiz_id, payload=None):
        return None


@receiver(post_save, sender=QuestionAttempt)
def update_score_and_leaderboard(sender, instance: QuestionAttempt, **kwargs):
    submission = instance.submission
    recompute_score(submission)
    invalidate_leaderboard(submission.quiz_id)
    broadcast_leaderboard(submission.quiz_id)
