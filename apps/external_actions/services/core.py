from __future__ import annotations

from typing import Any

from apps.external_actions.models import ExternalActionIntent


TERMINAL_APPROVAL_STATUSES = {
    ExternalActionIntent.ApprovalStatus.REJECTED,
    ExternalActionIntent.ApprovalStatus.EXPIRED,
}

TERMINAL_EXECUTION_STATUSES = {
    ExternalActionIntent.ExecutionStatus.SUCCEEDED,
    ExternalActionIntent.ExecutionStatus.FAILED,
    ExternalActionIntent.ExecutionStatus.SUPERSEDED,
}


def _normalize_policy(
    *,
    policy_classification: str | None = None,
    approval_required: bool | None = None,
) -> tuple[str, bool]:
    classification = (
        policy_classification
        or ExternalActionIntent.PolicyClassification.REVIEWABLE
    )

    if approval_required is None:
        approval_required = classification != ExternalActionIntent.PolicyClassification.AUTOMATIC

    return classification, bool(approval_required)


def _apply_initial_state(intent: ExternalActionIntent) -> ExternalActionIntent:
    if intent.approval_required:
        intent.mark_pending_approval()
        intent.dispatch_status = ExternalActionIntent.DispatchStatus.NOT_DISPATCHED
        intent.execution_status = ExternalActionIntent.ExecutionStatus.DRAFT
    else:
        intent.approval_required = False
        intent.approval_status = ExternalActionIntent.ApprovalStatus.NOT_REQUIRED
        intent.mark_ready()

    return intent


def _find_existing_by_idempotency(
    *,
    idempotency_key: str,
    idempotency_scope: str = "provider_account",
) -> ExternalActionIntent | None:
    if not idempotency_key:
        return None

    return (
        ExternalActionIntent.objects.filter(
            idempotency_key=idempotency_key,
            idempotency_scope=idempotency_scope,
        )
        .exclude(approval_status__in=TERMINAL_APPROVAL_STATUSES)
        .exclude(execution_status__in=TERMINAL_EXECUTION_STATUSES)
        .order_by("-created_at")
        .first()
    )


def create_external_action_intent(
    *,
    intent_type: str,
    payload: dict[str, Any] | None = None,
    port_name: str = "",
    adapter_key: str = "",
    provider: str = "",
    target_ref_type: str = "",
    target_ref_id: str = "",
    source_kind: str = ExternalActionIntent.SourceKind.RECOMMENDATION,
    source_id: str = "",
    recommendation=None,
    task=None,
    requested_by=None,
    normalized_preview: dict[str, Any] | None = None,
    policy_classification: str | None = None,
    approval_required: bool | None = None,
    idempotency_key: str = "",
    idempotency_scope: str = "provider_account",
    risk_score=None,
    reason: str = "",
    rationale: str = "",
    confidence=None,
    dry_run_supported: bool = True,
) -> ExternalActionIntent:
    existing = _find_existing_by_idempotency(
        idempotency_key=idempotency_key,
        idempotency_scope=idempotency_scope,
    )
    if existing is not None:
        return existing

    policy_classification, approval_required = _normalize_policy(
        policy_classification=policy_classification,
        approval_required=approval_required,
    )

    intent = ExternalActionIntent(
        intent_type=intent_type,
        port_name=port_name,
        adapter_key=adapter_key,
        provider=provider,
        target_ref_type=target_ref_type,
        target_ref_id=target_ref_id,
        source_kind=source_kind,
        source_id=str(source_id or ""),
        recommendation=recommendation,
        task=task,
        requested_by=requested_by,
        payload=payload or {},
        normalized_preview=normalized_preview or {},
        policy_classification=policy_classification,
        approval_required=approval_required,
        idempotency_key=idempotency_key,
        idempotency_scope=idempotency_scope,
        risk_score=risk_score,
        reason=reason,
        rationale=rationale,
        confidence=confidence,
        dry_run_supported=dry_run_supported,
    )

    _apply_initial_state(intent)
    intent.save()

    print(
        f"[FLOW] ExternalActionIntent created id={intent.id} "
        f"type={intent.intent_type} approval={intent.approval_status} "
        f"dispatch={intent.dispatch_status} execution={intent.execution_status}"
    )
    return intent
