from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.knowledge.services.hooks import on_external_action_executed


try:
    from apps.external_actions.models import ExternalActionIntent
except Exception:
    ExternalActionIntent = None


if ExternalActionIntent is not None:

    @receiver(post_save, sender=ExternalActionIntent)
    def knowledge_external_action_hook(sender, instance, created, **kwargs):
        try:
            on_external_action_executed(instance)
        except Exception:
            # Nunca debe romper el flujo principal de external actions.
            return
