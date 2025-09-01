from django.core.cache import cache

CACHE_KEY = "leaderboard:%s"
CACHE_TIMEOUT = 30  # seconds


def get_leaderboard(quiz_id: int):
    # Lazy import to avoid AppRegistryNotReady during ASGI import chain
    from submissions.models import Submission  # noqa
    key = CACHE_KEY % quiz_id
    data = cache.get(key)
    if data is not None:
        return data
    rows = (
        Submission.objects.filter(quiz_id=quiz_id, in_progress=False)
        .select_related("user")
        .order_by("-score", "submitted_at")[:10]
    )
    data = [
        {
            "user": s.user.username,
            "score": s.score,
            "attempt": s.attempt_number,
            "submitted_at": s.submitted_at.isoformat(),
        }
        for s in rows
    ]
    cache.set(key, data, CACHE_TIMEOUT)
    return data


def invalidate_leaderboard(quiz_id: int):
    cache.delete(CACHE_KEY % quiz_id)
