from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.dispatcher import dispatch_external_action_intent as run_external_action_dispatch
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
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
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
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
# no rompemos el flujo principal
            pass

    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
# no rompemos el flujo principal
            pass

    return intent


@transaction.atomic
def dispatch_external_action_intent(intent: ExternalActionIntent):
    return 

