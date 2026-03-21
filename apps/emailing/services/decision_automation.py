# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/services/decision_automation.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
import logging
from decimal import Decimal

from django.conf import settings

from apps.emailing.models import InboundDecision

logger = logging.getLogger(__name__)


def _confidence_as_float(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def score_inbound_decision(interpretation, decision_result):
    score = 0.0
    risk_flags = []

    confidence = _confidence_as_float(getattr(interpretation, "confidence", 0.0))
    intent = getattr(interpretation, "intent", "")
    urgency = getattr(interpretation, "urgency", "")
    sentiment = getattr(interpretation, "sentiment", "")
    action_type = getattr(decision_result, "action_type", "")
    requires_approval = bool(getattr(decision_result, "requires_approval", True))

    intent_weights = {
        "interested": 30,
        "objection": 20,
        "delay": 15,
        "rejection": 5,
        "unclear": 0,
    }
    urgency_weights = {
        "high": 20,
        "medium": 10,
        "low": 0,
    }
    sentiment_weights = {
        "positive": 15,
        "neutral": 5,
        "negative": 0,
    }
    action_weights = {
        InboundDecision.ACTION_SEND_INFORMATION: 5,
        InboundDecision.ACTION_SEND_CLARIFICATION: 5,
        InboundDecision.ACTION_SCHEDULE_FOLLOWUP: 12,
        InboundDecision.ACTION_ADVANCE_OPPORTUNITY: 10,
        InboundDecision.ACTION_MARK_LOST: 0,
    }

    score += intent_weights.get(intent, 0)
    score += urgency_weights.get(urgency, 0)
    score += sentiment_weights.get(sentiment, 0)
    score += confidence * 40
    score += action_weights.get(action_type, 0)

    if confidence < 0.60:
        risk_flags.append("low_confidence")

    if intent == "unclear":
        risk_flags.append("unclear_intent")

    if sentiment == "negative":
        risk_flags.append("negative_sentiment")

    if requires_approval:
        risk_flags.append("requires_approval")

    if action_type in getattr(settings, "INBOX_AUTO_BLOCKED_ACTIONS", []):
        risk_flags.append("blocked_action")

    if action_type == InboundDecision.ACTION_ADVANCE_OPPORTUNITY:
        risk_flags.append("sensitive_stage_change")

    score = max(0.0, min(round(score, 2), 100.0))

    if score >= 75:
        priority = InboundDecision.PRIORITY_HIGH
    elif score >= 45:
        priority = InboundDecision.PRIORITY_MEDIUM
    else:
        priority = InboundDecision.PRIORITY_LOW

    return score, priority, risk_flags


def should_auto_apply(decision: InboundDecision):
    if not getattr(settings, "INBOX_AUTO_APPLY_ENABLED", False):
        return False, "auto_apply_disabled"

    if decision.status != InboundDecision.STATUS_SUGGESTED:
        return False, f"decision_not_suggested:{decision.status}"

    if decision.requires_approval:
        return False, "requires_approval"

    if decision.action_type in getattr(settings, "INBOX_AUTO_BLOCKED_ACTIONS", []):
        return False, f"blocked_action:{decision.action_type}"

    threshold = float(getattr(settings, "INBOX_AUTO_APPLY_SCORE_THRESHOLD", 60))
    if float(decision.score) < threshold:
        return False, f"score_below_threshold:{decision.score}<{threshold}"

    blocking_flags = set(getattr(settings, "INBOX_AUTO_BLOCK_ON_RISK_FLAGS", []))
    active_flags = set(decision.risk_flags or [])
    matched_flags = sorted(blocking_flags.intersection(active_flags))
    if matched_flags:
        return False, f"risk_flags:{','.join(matched_flags)}"

    return True, f"score={decision.score}"


def maybe_auto_apply_decision(decision: InboundDecision):
    from apps.emailing.services.inbound_decision_apply_service import apply_inbound_decision

    allowed, reason = should_auto_apply(decision)

    if not allowed:
        logger.info(
            "Auto-apply blocked for decision %s (inbound=%s): %s",
            decision.id,
            decision.inbound_email_id,
            reason,
        )
        if decision.automation_reason != reason:
            decision.automation_reason = reason
            decision.save(update_fields=["automation_reason"])
        return {
            "auto_applied": False,
            "reason": reason,
            "decision_id": decision.id,
        }

    logger.info(
        "Auto-applying decision %s (inbound=%s): %s",
        decision.id,
        decision.inbound_email_id,
        reason,
    )
    result = apply_inbound_decision(
        decision,
        automatic=True,
        automation_reason=reason,
    )
    result["auto_applied"] = True
    result["reason"] = reason
    return result
