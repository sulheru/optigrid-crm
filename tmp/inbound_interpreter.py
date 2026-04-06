# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/services/inbound_interpreter.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class InboundInterpretationResult:
    intent: str
    urgency: str
    sentiment: str
    recommended_action: str
    confidence: float
    rationale: str
    signals: dict[str, Any]


REPLY_TYPE_TO_INTENT = {
    "interested": "interested",
    "needs_info": "objection",
    "not_now": "delay",
    "not_interested": "rejection",
    "unclear": "unclear",
}

INTENT_TO_ACTION = {
    "interested": "advance_opportunity",
    "objection": "send_information",
    "delay": "schedule_followup",
    "rejection": "mark_lost",
    "unclear": "send_clarification",
}


def _normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _detect_urgency(reply_type: str, body: str) -> tuple[str, dict[str, Any]]:
    text = _normalize_text(body)
    matched_keywords: list[str] = []

    urgency_keywords = [
        "urgent",
        "asap",
        "today",
        "tomorrow",
        "this week",
        "soon",
        "urgente",
        "hoy",
        "mañana",
        "esta semana",
        "cuanto antes",
    ]

    for keyword in urgency_keywords:
        if keyword in text:
            matched_keywords.append(keyword)

    if matched_keywords:
        return "high", {"urgent_keywords": matched_keywords}

    if reply_type == "interested":
        return "medium", {"urgent_keywords": []}

    if reply_type in {"not_now", "not_interested"}:
        return "low", {"urgent_keywords": []}

    return "medium", {"urgent_keywords": []}


def _detect_sentiment(reply_type: str, body: str) -> str:
    text = _normalize_text(body)

    positive_markers = [
        "interested",
        "sounds good",
        "let's talk",
        "looks good",
        "interesa",
        "me interesa",
        "perfecto",
        "bien",
    ]
    negative_markers = [
        "not interested",
        "no thanks",
        "stop",
        "remove me",
        "no interesa",
        "no gracias",
    ]

    if reply_type == "not_interested":
        return "negative"

    if any(marker in text for marker in negative_markers):
        return "negative"

    if reply_type == "interested":
        return "positive"

    if any(marker in text for marker in positive_markers):
        return "positive"

    return "neutral"


def _build_rationale(
    *,
    reply_type: str,
    intent: str,
    urgency: str,
    sentiment: str,
) -> str:
    return (
        f"reply_type={reply_type} mapped to intent={intent}; "
        f"urgency={urgency}; sentiment={sentiment}."
    )


def interpret_inbound_email(inbound_email) -> InboundInterpretationResult:
    reply_type = getattr(inbound_email, "reply_type", "") or "unclear"
    body = getattr(inbound_email, "body", "") or ""

    intent = REPLY_TYPE_TO_INTENT.get(reply_type, "unclear")
    recommended_action = INTENT_TO_ACTION[intent]
    urgency, urgency_signals = _detect_urgency(reply_type, body)
    sentiment = _detect_sentiment(reply_type, body)
    confidence = 0.90 if reply_type in REPLY_TYPE_TO_INTENT else 0.55

    signals: dict[str, Any] = {
        "reply_type": reply_type,
        **urgency_signals,
    }

    return InboundInterpretationResult(
        intent=intent,
        urgency=urgency,
        sentiment=sentiment,
        recommended_action=recommended_action,
        confidence=confidence,
        rationale=_build_rationale(
            reply_type=reply_type,
            intent=intent,
            urgency=urgency,
            sentiment=sentiment,
        ),
        signals=signals,
    )


def interpretation_to_dict(result: InboundInterpretationResult) -> dict[str, Any]:
    return asdict(result)
