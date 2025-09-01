from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'submissions'
    def ready(self):  # noqa: D401
        # Import signals to connect handlers
        from . import signals  # noqa: F401
