# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/opportunity_intelligence.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from django.db import transaction

from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.recommendations.models import AIRecommendation


OPPORTUNITY_REVIEW_TYPE = "opportunity_review"
ACTIVE_RECOMMENDATION_STATUSES = {"new", "active"}
DISMISSLIKE_STATUSES = {"dismissed", "executed", "materialized"}


@dataclass
class SignalAssessment:
    source_type: str
    source_id: int
    score: int
    confidence: float
    signals: list[str] = field(default_factory=list)
    rationale: str = ""
    should_create: bool = False


FACT_SCORES: dict[str, int] = {
    "scope_statement": 20,
    "budget_statement": 25,
    "scheduling_statement": 25,
    "interest_statement": 20,
    "redirect_statement": 5,
    "role_statement": 5,
    "light_reply_statement": -20,
}

INFERENCE_SCORES: dict[str, int] = {
    "opportunity_probability": 20,
    "interest_level": 15,
    "urgency_level": 10,
    "contact_role_fit": 5,
}


def _safe_lower(value: object) -> str:
    return str(value or "").strip().lower()


def _extract_signal_bonus_from_inference(inference: InferenceRecord) -> int:
    inference_type = _safe_lower(getattr(inference, "inference_type", ""))
    base = INFERENCE_SCORES.get(inference_type, 0)
    if base <= 0:
        return 0

    inference_value = getattr(inference, "inference_value", None)

    # Ajuste simple por contenido semántico
    text = _safe_lower(inference_value)
    if inference_type == "opportunity_probability":
        if any(token in text for token in ("high", "alta", "strong", "fuerte", "likely")):
            return base
        if any(token in text for token in ("medium", "media", "moderate")):
            return int(base * 0.6)
        return int(base * 0.4)

    if inference_type == "interest_level":
        if any(token in text for token in ("high", "alta", "strong", "fuerte")):
            return base
        if any(token in text for token in ("medium", "media", "moderate")):
            return int(base * 0.6)
        return int(base * 0.3)

    if inference_type == "urgency_level":
        if any(token in text for token in ("high", "alta", "urgent", "urgente")):
            return base
        if any(token in text for token in ("medium", "media")):
            return int(base * 0.5)
        return int(base * 0.2)

    return base


def _collect_facts(source_type: str, source_id: int) -> Iterable[FactRecord]:
    return FactRecord.objects.filter(source_type=source_type, source_id=source_id).order_by("id")


def _collect_inferences(source_type: str, source_id: int) -> Iterable[InferenceRecord]:
    return InferenceRecord.objects.filter(source_type=source_type, source_id=source_id).order_by("id")


def assess_source_for_opportunity(source_type: str, source_id: int) -> SignalAssessment:
    facts = list(_collect_facts(source_type=source_type, source_id=source_id))
    inferences = list(_collect_inferences(source_type=source_type, source_id=source_id))

    score = 0
    signals: list[str] = []

    for fact in facts:
        fact_type = _safe_lower(getattr(fact, "fact_type", ""))
        delta = FACT_SCORES.get(fact_type, 0)
        if delta != 0:
            score += delta
            signals.append(f"fact:{fact_type}")

    for inference in inferences:
        inference_type = _safe_lower(getattr(inference, "inference_type", ""))
        delta = _extract_signal_bonus_from_inference(inference)
        if delta != 0:
            score += delta
            signals.append(f"inference:{inference_type}")

    # Regla básica de umbral
    should_create = score >= 50

    # Confidence simple y estable
    confidence = min(max(score / 100.0, 0.05), 0.95)

    rationale_parts: list[str] = []
    if signals:
        rationale_parts.append("signals=" + ", ".join(signals))
    rationale_parts.append(f"score={score}")

    if score >= 70:
        rationale_parts.append("signal_strength=high")
    elif score >= 50:
        rationale_parts.append("signal_strength=medium")
    elif score >= 30:
        rationale_parts.append("signal_strength=weak")
    else:
        rationale_parts.append("signal_strength=insufficient")

    if should_create:
        rationale_parts.append(
            "decision=create opportunity_review recommendation"
        )
    else:
        rationale_parts.append(
            "decision=do not create opportunity_review recommendation"
        )

    return SignalAssessment(
        source_type=source_type,
        source_id=source_id,
        score=score,
        confidence=round(confidence, 2),
        signals=signals,
        rationale=" | ".join(rationale_parts),
        should_create=should_create,
    )


def _existing_recommendation(source_type: str, source_id: int):
    return AIRecommendation.objects.filter(
        scope_type=source_type,
        scope_id=source_id,
        recommendation_type=OPPORTUNITY_REVIEW_TYPE,
    ).exclude(status__in=DISMISSLIKE_STATUSES).order_by("-id").first()


@transaction.atomic
def ensure_opportunity_review_recommendation(source_type: str, source_id: int) -> tuple[AIRecommendation | None, bool, SignalAssessment]:
    assessment = assess_source_for_opportunity(source_type=source_type, source_id=source_id)

    existing = _existing_recommendation(source_type=source_type, source_id=source_id)
    if existing is not None:
        return existing, False, assessment

    if not assessment.should_create:
        return None, False, assessment

    recommendation_text = (
        "Se detecta señal comercial suficiente para revisar apertura de oportunidad. "
        f"(score={assessment.score})"
    )

    recommendation = AIRecommendation.objects.create(
        scope_type=source_type,
        scope_id=source_id,
        recommendation_type=OPPORTUNITY_REVIEW_TYPE,
        recommendation_text=recommendation_text,
        confidence=assessment.confidence,
        status="new",
    )

    return recommendation, True, assessment
