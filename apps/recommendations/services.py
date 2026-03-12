from apps.inferences.models import InferenceRecord
from apps.recommendations.models import AIRecommendation


OPPORTUNITY_SIGNAL_INFERENCE_TYPES = {
    "commercial_interest",
    "high_intent",
    "proposal_interest",
    "pricing_interest",
    "qualification_positive",
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

            interest_level = payload.get("interest_level")
            if interest_level in ("medium", "high"):
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
