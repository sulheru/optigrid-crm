from django.utils import timezone

from apps.external_actions.models import ExternalActionIntent


def approve_external_action_intent(intent: ExternalActionIntent, user) -> ExternalActionIntent:
    if not intent.approval_required:
        raise ValueError("Este intent no requiere aprobación")

    intent.approval_status = ExternalActionIntent.ApprovalStatus.APPROVED
    intent.approved_by = user
    intent.approved_at = timezone.now()
    intent.save()

    return intent
