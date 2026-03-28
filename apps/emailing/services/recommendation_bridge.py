from __future__ import annotations

from apps.recommendations.models import AIRecommendation
from apps.recommendations.services.factory import create_recommendation


ACTIVE_STATUSES = {
    AIRecommendation.STATUS_NEW,
    AIRecommendation.STATUS_MATERIALIZED,
}


ACTION_TYPE_TO_RECOMMENDATION_TYPE = {
    "send_information": "reply_strategy",
    "send_clarification": "reply_strategy",
    "schedule_followup": "followup",
    "advance_opportunity": "advance_opportunity",
    "mark_lost": "mark_lost",
}


def create_email_recommendation(
    *,
    email_message,
    recommendation_type: str,
    recommendation_text: str,
    confidence: float,
    source: str = AIRecommendation.SOURCE_RULES,
):
    return create_recommendation(
        scope_type="email_message",
        scope_id=email_message.id,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=confidence,
        source=source,
        status=AIRecommendation.STATUS_NEW,
    )


def _infer_scope_id(inbound_decision) -> str:
    inbound_email_id = getattr(inbound_decision, "inbound_email_id", None)
    if inbound_email_id is None:
        raise ValueError("InboundDecision sin inbound_email_id para recommendation bridge")
    return str(inbound_email_id)


def _infer_recommendation_type(inbound_decision) -> str:
    action_type = str(getattr(inbound_decision, "action_type", "") or "").strip().lower()
    if action_type:
        return ACTION_TYPE_TO_RECOMMENDATION_TYPE.get(action_type, action_type)

    candidates = [
        getattr(inbound_decision, "recommended_task_type", None),
        getattr(inbound_decision, "task_type", None),
        getattr(inbound_decision, "decision_type", None),
        getattr(inbound_decision, "decision", None),
        getattr(inbound_decision, "automation_action", None),
    ]
    for value in candidates:
        text = str(value or "").strip()
        if text:
            return text
    return "review_manually"


def _infer_recommendation_text(inbound_decision) -> str:
    candidates = [
        getattr(inbound_decision, "recommendation_text", None),
        getattr(inbound_decision, "reason", None),
        getattr(inbound_decision, "rationale", None),
        getattr(inbound_decision, "summary", None),
        getattr(inbound_decision, "notes", None),
    ]
    for value in candidates:
        text = str(value or "").strip()
        if text:
            return text

    action_type = str(getattr(inbound_decision, "action_type", "") or "").strip().lower()
    defaults = {
        "send_information": "Responder con la información solicitada por el contacto.",
        "send_clarification": "Responder aclarando la información solicitada.",
        "schedule_followup": "Programar seguimiento comercial.",
        "advance_opportunity": "Avanzar la oportunidad a la siguiente fase.",
        "mark_lost": "Marcar la oportunidad como perdida.",
    }
    return defaults.get(action_type, "Review inbound decision")


def _infer_confidence(inbound_decision) -> float:
    value = getattr(inbound_decision, "confidence", None)
    try:
        if value is None:
            return 0.5
        return float(value)
    except Exception:
        return 0.5


def ensure_recommendation_for_inbound_decision(
    inbound_decision,
    *,
    source: str = AIRecommendation.SOURCE_RULES,
):
    scope_type = "inbound_email"
    scope_id = _infer_scope_id(inbound_decision)
    recommendation_type = _infer_recommendation_type(inbound_decision)
    recommendation_text = _infer_recommendation_text(inbound_decision)
    confidence = _infer_confidence(inbound_decision)

    existing = (
        AIRecommendation.objects.filter(
            scope_type=scope_type,
            scope_id=scope_id,
            recommendation_type=recommendation_type,
            status__in=ACTIVE_STATUSES,
        )
        .order_by("-id")
        .first()
    )
    if existing is not None:
        return existing

    return create_recommendation(
        scope_type=scope_type,
        scope_id=scope_id,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=confidence,
        source=source,
        status=AIRecommendation.STATUS_NEW,
    )
