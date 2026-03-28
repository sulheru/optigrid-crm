from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.knowledge"
    verbose_name = "Knowledge"

    def ready(self):
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Nunca debe romper el arranque por el hook de conocimiento.
            pass
