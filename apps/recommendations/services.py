from __future__ import annotations

from apps.inferences.models import InferenceRecord
from apps.recommendations.models import AIRecommendation


OPPORTUNITY_SIGNAL_INFERENCE_TYPES = {
    "commercial_interest",
    "high_intent",
    "proposal_interest",
    "pricing_interest",
    "qualification_positive",
}

RECOMMENDATION_TYPE_MAP = {
    "find_alternative_contact": "contact_strategy",
    "follow_up_later": "followup",
    "reply_with_scope_clarification": "reply_strategy",
}


def _related_inferences(scope_type: str, scope_id: int):
    if not scope_type or scope_id in (None, ""):
        return InferenceRecord.objects.none()

    if scope_type == "inference_record":
        return InferenceRecord.objects.filter(pk=scope_id)

    return InferenceRecord.objects.filter(
        source_type=scope_type,
        source_id=scope_id,
    )


def should_create_opportunity_review(scope_type: str, scope_id: int) -> tuple[bool, list[str]]:
    reasons = []
    related_inferences = _related_inferences(scope_type, scope_id)

    signal_count = 0
    for inference in related_inferences:
        inference_type = (getattr(inference, "inference_type", "") or "").strip().lower()
        if inference_type in OPPORTUNITY_SIGNAL_INFERENCE_TYPES:
            signal_count += 1
            reasons.append(f"inference:{inference_type}")
            continue

        payload = getattr(inference, "inference_value", None) or {}
        if isinstance(payload, dict):
            signal = payload.get("commercial_signal")
            if signal in ("pricing", "proposal", "meeting", "scope"):
                signal_count += 1
                reasons.append(f"commercial_signal:{signal}")
                continue

            interest_level = payload.get("interest_level") or payload.get("level")
            if interest_level in ("medium", "moderate", "high"):
                signal_count += 1
                reasons.append(f"interest_level:{interest_level}")

    if signal_count >= 1:
        return True, reasons

    return False, reasons


def create_recommendation(
    *,
    scope_type: str,
    scope_id: int,
    recommendation_type: str,
    recommendation_text: str,
    confidence: float = 0.70,
):
    return AIRecommendation.objects.create(
        scope_type=scope_type,
        scope_id=scope_id,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=confidence,
        status="new",
    )


def maybe_create_opportunity_review(scope_type: str, scope_id: int):
    exists = AIRecommendation.objects.filter(
        scope_type=scope_type,
        scope_id=scope_id,
        recommendation_type="opportunity_review",
    ).exists()
    if exists:
        return None

    should_create, reasons = should_create_opportunity_review(scope_type, scope_id)
    if not should_create:
        return None

    reason_text = ", ".join(reasons[:3]) if reasons else "commercial signals detected"

    return create_recommendation(
        scope_type=scope_type,
        scope_id=scope_id,
        recommendation_type="opportunity_review",
        recommendation_text=f"Revisar oportunidad comercial detectada por señales: {reason_text}.",
        confidence=0.80,
    )


def _recommendation_text_for_inference(inference: InferenceRecord) -> tuple[str, str, float] | None:
    inference_type = (getattr(inference, "inference_type", "") or "").strip().lower()
    payload = getattr(inference, "inference_value", None) or {}
    confidence = float(getattr(inference, "confidence", 0.70) or 0.70)

    if inference_type == "next_best_action":
        action = (payload.get("action") or "").strip().lower()
        recommendation_type = RECOMMENDATION_TYPE_MAP.get(action)
        if not recommendation_type:
            return None

        if action == "find_alternative_contact":
            return (
                recommendation_type,
                "Buscar un contacto alternativo o redirigido para continuar la conversación comercial.",
                confidence,
            )

        if action == "follow_up_later":
            timing = payload.get("suggested_timing") or "más adelante"
            return (
                recommendation_type,
                f"Programar follow-up posterior. Ventana sugerida: {timing}.",
                confidence,
            )

        if action == "reply_with_scope_clarification":
            return (
                recommendation_type,
                "Responder con aclaración de alcance para mantener el avance comercial.",
                confidence,
            )

    if inference_type == "contact_role_fit":
        status = (payload.get("status") or "").strip().lower()
        if status == "redirected":
            return (
                "contact_strategy",
                "Revisar estrategia de contacto y localizar al interlocutor correcto.",
                confidence,
            )

    if inference_type == "interest_level":
        level = (payload.get("level") or "").strip().lower()
        if level in {"moderate", "high"}:
            return (
                "opportunity_review",
                "Revisar si existe una oportunidad comercial activa a partir del interés detectado.",
                confidence,
            )

    if inference_type == "opportunity_probability":
        status = (payload.get("status") or "").strip().lower()
        if status == "emerging_signal":
            return (
                "opportunity_review",
                "Revisar señal de oportunidad emergente detectada en la conversación.",
                confidence,
            )

    if inference_type == "pricing_objection":
        return (
            "pricing_strategy",
            "Revisar estrategia de pricing o sensibilidad presupuestaria detectada.",
            confidence,
        )

    if inference_type == "relationship_temperature":
        temperature = (payload.get("temperature") or "").strip().lower()
        if temperature == "deferred_not_rejected":
            return (
                "followup",
                "Mantener relación activa con follow-up diferido, sin tratarlo como rechazo.",
                confidence,
            )

    return None


def create_recommendation_from_inference(inference: InferenceRecord):
    spec = _recommendation_text_for_inference(inference)
    if not spec:
        return None

    recommendation_type, recommendation_text, confidence = spec

    existing = AIRecommendation.objects.filter(
        scope_type="inference_record",
        scope_id=inference.id,
        recommendation_type=recommendation_type,
    ).first()
    if existing:
        return existing

    return create_recommendation(
        scope_type="inference_record",
        scope_id=inference.id,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=confidence,
    )
