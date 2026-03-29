from __future__ import annotations

from typing import Any

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services import create_external_action_intent
from apps.recommendations.execution_adapters import prepare_mail_provider_context


MAIL_DRAFT_RECOMMENDATION_TYPES = {
    "followup",
    "reply_strategy",
    "contact_strategy",
}


def recommendation_supports_external_intent(recommendation) -> bool:
    recommendation_type = getattr(recommendation, "recommendation_type", "") or ""
    return recommendation_type in MAIL_DRAFT_RECOMMENDATION_TYPES


def map_recommendation_to_external_intent_spec(recommendation) -> dict[str, Any] | None:
    recommendation_type = getattr(recommendation, "recommendation_type", "") or ""

    if recommendation_type in MAIL_DRAFT_RECOMMENDATION_TYPES:
        return {
            "intent_type": ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            "port_name": "mail",
            "provider": "m365",
            "target_ref_type": "recommendation",
            "target_ref_id": str(getattr(recommendation, "pk", "") or ""),
        }

    return None


def build_mail_payload_from_recommendation(recommendation) -> dict[str, Any]:
    content = getattr(recommendation, "content", "") or ""
    rationale = getattr(recommendation, "rationale", "") or ""
    title = getattr(recommendation, "title", "") or ""
    recommendation_type = getattr(recommendation, "recommendation_type", "") or ""

    subject = title or f"AI draft for {recommendation_type}"
    body_parts = [part for part in [content, rationale] if part]
    body = "\n\n".join(body_parts).strip()

    to = []
    contact_email = _extract_contact_email(recommendation)
    if contact_email:
        to = [contact_email]

    inbound_email = _resolve_inbound_email(recommendation)
    thread_ref = _extract_thread_ref(recommendation, inbound_email=inbound_email)
    account_key = _extract_account_key(recommendation, inbound_email=inbound_email)

    return prepare_mail_provider_context(
        subject=subject[:255] if subject else f"AI draft for {recommendation_type}",
        body=body,
        to=to,
        thread_ref=thread_ref,
        account_key=account_key,
        metadata={
            "source_recommendation_id": getattr(recommendation, "pk", None),
            "recommendation_type": recommendation_type,
            "thread_ref": thread_ref,
            "mail_account_key": account_key,
            "resolved_from_inbound": bool(inbound_email),
            "inbound_email_id": getattr(inbound_email, "pk", None) if inbound_email else None,
        },
    )


def build_normalized_preview_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "channel": "mail",
        "mode": "create_draft",
        "provider": payload.get("provider", ""),
        "account_key": payload.get("account_key", ""),
        "provider_status": payload.get("provider_status", ""),
        "external_draft_id": payload.get("external_draft_id"),
        "to": payload.get("to", []),
        "cc": payload.get("cc", []),
        "bcc": payload.get("bcc", []),
        "subject": payload.get("subject", ""),
        "thread_ref": payload.get("thread_ref"),
        "resolved_from_inbound": (payload.get("metadata") or {}).get("resolved_from_inbound", False),
        "inbound_email_id": (payload.get("metadata") or {}).get("inbound_email_id"),
    }


def _extract_contact_email(recommendation) -> str | None:
    for attr in ("contact", "target_contact", "related_contact"):
        obj = getattr(recommendation, attr, None)
        if obj is not None:
            email = getattr(obj, "email", None)
            if email:
                return email

    for attr in ("email_to", "target_email", "recipient_email"):
        value = getattr(recommendation, attr, None)
        if value:
            return value

    metadata = getattr(recommendation, "metadata", None)
    if isinstance(metadata, dict):
        for key in ("email", "to", "recipient_email", "target_email"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def _resolve_inbound_email(recommendation):
    for attr in ("inbound_email", "source_inbound", "related_inbound_email", "email"):
        obj = getattr(recommendation, attr, None)
        if obj is not None:
            return obj

    metadata = getattr(recommendation, "metadata", None)
    if isinstance(metadata, dict):
        candidate_id = metadata.get("inbound_email_id") or metadata.get("source_inbound_id")
        obj = _load_inbound_email_by_id(candidate_id)
        if obj is not None:
            return obj

    scope_type = getattr(recommendation, "scope_type", "") or ""
    scope_id = getattr(recommendation, "scope_id", None)
    if scope_type == "inbound_email":
        obj = _load_inbound_email_by_id(scope_id)
        if obj is not None:
            return obj

    source_kind = getattr(recommendation, "source_kind", "") or ""
    source_id = getattr(recommendation, "source_id", None)
    if source_kind == "inbound_email":
        obj = _load_inbound_email_by_id(source_id)
        if obj is not None:
            return obj

    return None


def _load_inbound_email_by_id(value):
    if value in (None, ""):
        return None

    try:
        pk = int(value)
    except (TypeError, ValueError):
        return None

    try:
        from apps.emailing.models import InboundEmail
    except Exception:
        return None

    try:
        return InboundEmail.objects.filter(pk=pk).first()
    except Exception:
        return None


def _extract_thread_ref(recommendation, *, inbound_email=None) -> str | None:
    if inbound_email is not None:
        for attr in ("thread_id", "external_thread_ref", "thread_ref"):
            value = getattr(inbound_email, attr, None)
            if value:
                return str(value)

        thread = getattr(inbound_email, "thread", None)
        if thread is not None:
            for attr in ("pk", "id", "external_thread_ref", "thread_ref"):
                value = getattr(thread, attr, None)
                if value:
                    return str(value)

    for attr in ("thread_ref", "external_thread_ref"):
        value = getattr(recommendation, attr, None)
        if value:
            return str(value)

    metadata = getattr(recommendation, "metadata", None)
    if isinstance(metadata, dict):
        for key in ("thread_ref", "external_thread_ref", "thread_id"):
            value = metadata.get(key)
            if value:
                return str(value)

    return None


def _extract_account_key(recommendation, *, inbound_email=None) -> str | None:
    for attr in ("account_key", "mail_account_key", "provider_account_key"):
        value = getattr(recommendation, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()

    if inbound_email is not None:
        for attr in ("account_key", "mail_account_key", "provider_account_key", "mailbox_account_key"):
            value = getattr(inbound_email, attr, None)
            if isinstance(value, str) and value.strip():
                return value.strip()

        thread = getattr(inbound_email, "thread", None)
        if thread is not None:
            for attr in ("account_key", "mail_account_key", "provider_account_key", "mailbox_account_key"):
                value = getattr(thread, attr, None)
                if isinstance(value, str) and value.strip():
                    return value.strip()

    metadata = getattr(recommendation, "metadata", None)
    if isinstance(metadata, dict):
        for key in ("mail_account_key", "account_key", "provider_account_key"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def get_open_external_intent_for_recommendation(recommendation, intent_type: str):
    return (
        ExternalActionIntent.objects.filter(
            recommendation=recommendation,
            intent_type=intent_type,
        )
        .exclude(
            execution_status__in=[
                ExternalActionIntent.ExecutionStatus.SUCCEEDED,
                ExternalActionIntent.ExecutionStatus.SUPERSEDED,
            ]
        )
        .order_by("-created_at")
        .first()
    )


def ensure_external_action_intent_for_recommendation(recommendation, *, requested_by=None):
    spec = map_recommendation_to_external_intent_spec(recommendation)
    if not spec:
        return None, False

    existing = get_open_external_intent_for_recommendation(recommendation, spec["intent_type"])
    if existing is not None:
        return existing, False

    payload = build_mail_payload_from_recommendation(recommendation)
    normalized_preview = build_normalized_preview_from_payload(payload)

    intent = create_external_action_intent(
        intent_type=spec["intent_type"],
        port_name=spec["port_name"],
        provider=spec["provider"],
        payload=payload,
        source_kind=ExternalActionIntent.SourceKind.RECOMMENDATION,
        source_id=str(getattr(recommendation, "pk", "") or ""),
        recommendation=recommendation,
        requested_by=requested_by,
        target_ref_type=spec["target_ref_type"],
        target_ref_id=spec["target_ref_id"],
        rationale=getattr(recommendation, "rationale", "") or "",
        reason=f"Created from recommendation:{getattr(recommendation, 'recommendation_type', '')}",
        confidence=getattr(recommendation, "confidence", None),
    )

    intent.normalized_preview = normalized_preview
    intent.save(update_fields=["normalized_preview", "updated_at"])

    return intent, True
