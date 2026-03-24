from __future__ import annotations

from apps.emailing.models import InboundDecision
from apps.recommendations.models import AIRecommendation


ACTION_TO_RECOMMENDATION_TYPE = {
    InboundDecision.ACTION_SEND_INFORMATION: "reply_strategy",
    InboundDecision.ACTION_SEND_CLARIFICATION: "reply_strategy",
    InboundDecision.ACTION_SCHEDULE_FOLLOWUP: "followup",
    InboundDecision.ACTION_ADVANCE_OPPORTUNITY: "advance_opportunity",
    InboundDecision.ACTION_MARK_LOST: "mark_lost",
}


def ensure_recommendation_for_inbound_decision(decision: InboundDecision) -> AIRecommendation:
    recommendation_type = ACTION_TO_RECOMMENDATION_TYPE.get(decision.action_type, "reply_strategy")
    scope_type = "inbound_email"
    scope_id = decision.inbound_email_id
    recommendation_text = (decision.summary or "").strip() or f"Execute inbound decision: {decision.action_type}"
    confidence = 0.70

    interpretation = getattr(decision, "interpretation", None)
    if interpretation is not None:
        confidence = float(getattr(interpretation, "confidence", confidence) or confidence)

    existing = AIRecommendation.objects.filter(
        scope_type=scope_type,
        scope_id=scope_id,
        recommendation_type=recommendation_type,
    ).exclude(status="dismissed").order_by("-id").first()
    if existing:
        return existing

    return AIRecommendation.objects.create(
        scope_type=scope_type,
        scope_id=scope_id,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=confidence,
        status="new",
    )
