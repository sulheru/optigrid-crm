from __future__ import annotations

from apps.external_actions.models import ExternalActionIntent


def approve_external_action_intent(
    intent: ExternalActionIntent,
    user,
) -> ExternalActionIntent:
    if not intent.approval_required:
        raise ValueError("Este intent no requiere aprobación")

    if intent.approval_status == ExternalActionIntent.ApprovalStatus.APPROVED:
        return intent

    if intent.approval_status in {
        ExternalActionIntent.ApprovalStatus.REJECTED,
        ExternalActionIntent.ApprovalStatus.EXPIRED,
    }:
        raise ValueError("No se puede aprobar un intent rechazado o expirado")

    intent.mark_approved(user=user)
    intent.mark_ready()
    intent.save(
        update_fields=[
            "approval_required",
            "approval_status",
            "approved_by",
            "approved_at",
            "dispatch_status",
            "execution_status",
            "updated_at",
        ]
    )

    print(
        f"[FLOW] ExternalActionIntent approved id={intent.id} "
        f"type={intent.intent_type}"
    )
    return intent
