"""ASGI entrypoint wired for Django Channels."""
import os

# Configure settings module before importing Django/Channels components
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quiz_project.settings")

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402
from .routing import websocket_urlpatterns  # noqa: E402

# Serve static files via Channels helper when using Daphne in dev
try:  # pragma: no cover - best effort
	from channels.staticfiles import StaticFilesWrapper  # type: ignore
except Exception:  # pragma: no cover
	StaticFilesWrapper = None  # type: ignore

django_asgi_app = get_asgi_application()
http_app = StaticFilesWrapper(django_asgi_app) if StaticFilesWrapper else django_asgi_app

application = ProtocolTypeRouter({
	"http": http_app,
	"websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
