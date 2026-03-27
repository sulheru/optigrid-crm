from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.dispatcher import dispatch_external_action_intent
from services.ports.idempotency import build_intent_idempotency_key
from services.ports.policy import evaluate_policy_for_intent
from services.ports.router import get_port_router


@transaction.atomic
def create_external_action_intent(
    *,
    intent_type: str,
    port_name: str,
    payload: dict[str, Any],
    provider: str = "m365",
    source_kind: str = ExternalActionIntent.SourceKind.RECOMMENDATION,
    source_id: str = "",
    recommendation=None,
    task=None,
    requested_by=None,
    target_ref_type: str = "",
    target_ref_id: str = "",
    rationale: str = "",
    reason: str = "",
    confidence=None,
) -> ExternalActionIntent:
    intent = ExternalActionIntent.objects.create(
        intent_type=intent_type,
        port_name=port_name,
        provider=provider,
        source_kind=source_kind,
        source_id=source_id,
        recommendation=recommendation,
        task=task,
        requested_by=requested_by,
        target_ref_type=target_ref_type,
        target_ref_id=target_ref_id,
        payload=payload or {},
        rationale=rationale,
        reason=reason,
        confidence=confidence,
    )
    intent.idempotency_key = build_intent_idempotency_key(intent)
    decision = evaluate_policy_for_intent(intent)
    intent.policy_classification = decision.classification
    intent.approval_required = decision.requires_approval

    if decision.decision == "block":
        intent.mark_blocked("; ".join(decision.reasons) or "Blocked by policy.")
    elif decision.decision == "require_approval":
        intent.mark_pending_approval()
    else:
        intent.approval_status = ExternalActionIntent.ApprovalStatus.NOT_REQUIRED
        intent.mark_ready()

    intent.save()
    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    return intent


@transaction.atomic
def approve_external_action_intent(intent: ExternalActionIntent, *, approved_by=None) -> ExternalActionIntent:
    intent.mark_approved(user=approved_by)
    intent.mark_ready()
    intent.save(update_fields=[
        "approval_required",
        "approval_status",
        "approved_by",
        "approved_at",
        "dispatch_status",
        "execution_status",
        "updated_at",
    ])
    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    return intent


@transaction.atomic
def dispatch_external_action_intent(intent: ExternalActionIntent):
    if intent.requires_human_approval() and intent.approval_status != ExternalActionIntent.ApprovalStatus.APPROVED:
        intent.mark_blocked("Intent requires explicit human approval before dispatch.")
        intent.save(update_fields=["execution_status", "last_error_code", "last_error_message", "updated_at"])
        # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    return intent, None

    router = get_port_router()
    try:
        port = router.resolve(intent)
    except LookupError as exc:
        intent.mark_blocked(str(exc))
        intent.save(update_fields=["execution_status", "last_error_code", "last_error_message", "updated_at"])
        # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    return intent, None

    validation = port.validate(intent)
    if not validation.ok:
        intent.mark_blocked("; ".join(validation.errors) or "Validation failed.")
        intent.save(update_fields=["execution_status", "last_error_code", "last_error_message", "updated_at"])
        # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    return intent, None

    prepared = port.prepare(intent)
    intent.normalized_preview = prepared.preview or {}
    intent.adapter_key = port.adapter_key
    intent.mark_dispatched()
    intent.save(update_fields=[
        "normalized_preview",
        "adapter_key",
        "dispatch_status",
        "execution_status",
        "dispatched_at",
        "last_attempt_at",
        "attempt_count",
        "updated_at",
    ])

    provider_result = port.execute(prepared)
    normalized = port.normalize_result(provider_result)

    if normalized.status == "succeeded":
        intent.mark_succeeded()
        intent.last_error_code = ""
        intent.last_error_message = ""
        if normalized.raw:
            intent.normalized_preview = normalized.raw
    else:
        intent.mark_failed(
            normalized.error_code or "provider_failed",
            normalized.summary or normalized.error_code or "Provider execution failed.",
        )

    intent.save()
    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    return intent, normalized
