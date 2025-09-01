"""Stats middlewares for Prometheus metrics collection."""
from typing import Callable
from django.contrib.sessions.models import Session
from django.utils import timezone

from prometheus_client import Counter, Gauge

REQUEST_COUNTER = Counter('quizzy_http_requests_total', 'Total HTTP requests', ['method','path'])
ACTIVE_USERS = Gauge('quizzy_active_users', 'Active authenticated users (session window)')

class RequestMetricsMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if len(path) > 64:
            path = path[:60] + '...'
        response = self.get_response(request)
        try:
            REQUEST_COUNTER.labels(request.method, path).inc()
        except Exception:  # pragma: no cover
            pass
        return response

class ActiveUsersGaugeMiddleware:
    """Counts active authenticated sessions updated in last 30 minutes."""
    WINDOW_MINUTES = 30
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        resp = self.get_response(request)
        try:
            cutoff = timezone.now() - timezone.timedelta(minutes=self.WINDOW_MINUTES)
            count = Session.objects.filter(expire_date__gt=cutoff).count()
            ACTIVE_USERS.set(count)
        except Exception:  # pragma: no cover
            pass
        return resp
