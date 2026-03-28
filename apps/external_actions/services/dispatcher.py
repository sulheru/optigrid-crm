from __future__ import annotations

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.providers.email_stub import send_email_draft


BLOCKED_INTENT_TYPES = {
    ExternalActionIntent.IntentType.EMAIL_SEND,
}


def _ensure_dispatchable(intent: ExternalActionIntent) -> None:
    if intent.intent_type in BLOCKED_INTENT_TYPES:
        raise ValueError("Auto-send de email desactivado por guardrail global")

    if intent.execution_status == ExternalActionIntent.ExecutionStatus.EXECUTING:
        raise ValueError("El intent ya está en ejecución")

    if intent.dispatch_status == ExternalActionIntent.DispatchStatus.DISPATCHED:
        raise ValueError("El intent ya fue despachado")

    if intent.approval_required:
        if intent.approval_status != ExternalActionIntent.ApprovalStatus.APPROVED:
            raise ValueError("El intent requiere aprobación humana antes del dispatch")
    else:
        if intent.approval_status not in {
            ExternalActionIntent.ApprovalStatus.NOT_REQUIRED,
            ExternalActionIntent.ApprovalStatus.APPROVED,
        }:
            raise ValueError("Estado de aprobación no válido para dispatch")

    if intent.execution_status not in {
        ExternalActionIntent.ExecutionStatus.READY_TO_EXECUTE,
        ExternalActionIntent.ExecutionStatus.DRAFT,
        ExternalActionIntent.ExecutionStatus.VALIDATED,
        ExternalActionIntent.ExecutionStatus.DRY_RUN_READY,
    }:
        raise ValueError("El intent no está en un estado ejecutable")


def _perform_dispatch(intent: ExternalActionIntent) -> None:
    # Stub canónico único para esta fase.
    # Mantiene compatibilidad con los tests actuales y evita múltiples rutas activas.
    send_email_draft(intent.payload)


def dispatch_external_action_intent(intent: ExternalActionIntent) -> ExternalActionIntent:
    if intent.execution_status == ExternalActionIntent.ExecutionStatus.SUCCEEDED:
        return intent

    if intent.dispatch_status == ExternalActionIntent.DispatchStatus.COMPLETED:
        return intent

    _ensure_dispatchable(intent)

    try:
        intent.mark_dispatched()
        intent.save(
            update_fields=[
                "dispatch_status",
                "execution_status",
                "dispatched_at",
                "last_attempt_at",
                "attempt_count",
                "updated_at",
            ]
        )

        _perform_dispatch(intent)

        intent.mark_succeeded()
        intent.save(
            update_fields=[
                "dispatch_status",
                "execution_status",
                "completed_at",
                "updated_at",
            ]
        )

        print(
            f"[FLOW] ExternalActionIntent dispatched id={intent.id} "
            f"type={intent.intent_type}"
        )
        return intent

    except Exception as exc:
        intent.mark_failed(code="dispatch_error", message=str(exc))
        intent.save(
            update_fields=[
                "dispatch_status",
                "execution_status",
                "last_error_code",
                "last_error_message",
                "updated_at",
            ]
        )
        raise
