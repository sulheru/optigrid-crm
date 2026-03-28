from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.providers.email_stub import send_email_draft


def _model_fields():
    return {f.name for f in ExternalActionIntent._meta.fields}


def _has(field: str) -> bool:
    return field in _model_fields()


def _get_enum(container_name: str, attr_name: str, default: str):
    container = getattr(ExternalActionIntent, container_name, None)
    if not container:
        return default
    return getattr(container, attr_name, default)


def _set_execution_status(intent, value, update_fields):
    if _has("execution_status"):
        intent.execution_status = value
        update_fields.append("execution_status")
    elif _has("status"):
        intent.status = value
        update_fields.append("status")


def _set_error(intent, error, update_fields):
    if _has("error_message"):
        intent.error_message = error
        update_fields.append("error_message")


def _set_result(intent, result, update_fields):
    if _has("provider_result"):
        intent.provider_result = result
        update_fields.append("provider_result")


def _already_executed(intent: ExternalActionIntent) -> bool:
    if _has("execution_status"):
        return intent.execution_status == _get_enum("ExecutionStatus", "EXECUTED", "executed")
    if _has("status"):
        return intent.status == _get_enum("ExecutionStatus", "EXECUTED", "executed")
    return False


def _is_allowed(intent: ExternalActionIntent) -> bool:
    if not getattr(intent, "approval_required", False):
        return True
    return getattr(intent, "approval_status", None) == _get_enum("ApprovalStatus", "APPROVED", "approved")


def _resolve_handler(intent: ExternalActionIntent):
    return send_email_draft


def dispatch_external_action_intent(intent: ExternalActionIntent) -> ExternalActionIntent:

    # 🔒 Fase 1 — lock + ejecución (puede fallar → rollback OK)
    try:
        with transaction.atomic():
            intent = ExternalActionIntent.objects.select_for_update().get(pk=intent.pk)

            if _already_executed(intent):
                return intent

            if not _is_allowed(intent):
                raise ValueError("Este intent requiere aprobación antes de ejecutarse")

            result: dict[str, Any] = _resolve_handler(intent)(intent)

            update_fields = []
            _set_result(intent, result, update_fields)
            _set_execution_status(intent, _get_enum("ExecutionStatus", "EXECUTED", "executed"), update_fields)
            _set_error(intent, "", update_fields)

            intent.save(update_fields=update_fields or None)
            return intent

    except Exception as exc:

        # 🔒 Fase 2 — persistir fallo en NUEVA transacción
        with transaction.atomic():
            intent = ExternalActionIntent.objects.get(pk=intent.pk)

            update_fields = []
            _set_execution_status(intent, _get_enum("ExecutionStatus", "FAILED", "failed"), update_fields)
            _set_error(intent, str(exc), update_fields)

            intent.save(update_fields=update_fields or None)

        raise
