from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from django.db.models import QuerySet
from django.utils import timezone

from apps.recommendations.models import AIRecommendation


TYPE_WEIGHTS = {
    "followup": 1.0,
    "contact_strategy": 0.6,
    "opportunity_review": 0.5,
    "review": 0.3,
}


@dataclass(frozen=True)
class NBAResult:
    recommendation: AIRecommendation
    confidence_score: float
    urgency_score: float
    type_weight: float
    final_score: float


def get_type_weight(recommendation_type: str | None) -> float:
    if not recommendation_type:
        return 0.3
    return TYPE_WEIGHTS.get(recommendation_type, 0.3)


def get_urgency_score(recommendation: AIRecommendation) -> float:
    # V1 determinista, sin LLM.
    # Señales usadas:
    # - recencia
    # - hints textuales en rationale / text
    # - tipo followup como proxy de “sin respuesta / espera de acción”
    now = timezone.now()

    timestamps = [
        getattr(recommendation, "created_at", None),
        getattr(recommendation, "updated_at", None),
    ]
    timestamps = [ts for ts in timestamps if ts is not None]
    reference_ts = max(timestamps) if timestamps else None

    text_parts = [
        getattr(recommendation, "recommendation_text", "") or "",
        getattr(recommendation, "rationale", "") or "",
    ]
    text_blob = " ".join(text_parts).lower()

    recency_score = 0.2
    if reference_ts is not None:
        age = now - reference_ts
        if age <= timedelta(days=2):
            recency_score = 1.0
        elif age <= timedelta(days=7):
            recency_score = 0.7
        elif age <= timedelta(days=21):
            recency_score = 0.4
        else:
            recency_score = 0.2

    waiting_markers = [
        "no reply",
        "sin respuesta",
        "awaiting reply",
        "follow-up",
        "follow up",
        "seguimiento",
        "remind",
        "retomar",
    ]
    cold_markers = [
        "cold",
        "frío",
        "paused",
        "deferred",
        "later",
        "más adelante",
    ]

    if any(marker in text_blob for marker in waiting_markers):
        return max(recency_score, 0.6)

    if any(marker in text_blob for marker in cold_markers):
        return min(recency_score, 0.3)

    if getattr(recommendation, "recommendation_type", None) == "followup":
        return max(recency_score, 0.7)

    return recency_score


def get_recommendation_confidence(recommendation: AIRecommendation) -> float:
    raw = getattr(recommendation, "confidence", 0.0) or 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def score_recommendation(recommendation: AIRecommendation) -> NBAResult:
    confidence_score = get_recommendation_confidence(recommendation)
    urgency_score = get_urgency_score(recommendation)
    type_weight = get_type_weight(getattr(recommendation, "recommendation_type", None))
    final_score = confidence_score + urgency_score + type_weight

    return NBAResult(
        recommendation=recommendation,
        confidence_score=confidence_score,
        urgency_score=urgency_score,
        type_weight=type_weight,
        final_score=final_score,
    )


def _base_queryset() -> QuerySet[AIRecommendation]:
    qs = AIRecommendation.objects.all()

    status_field = getattr(AIRecommendation, "status", None)
    source_field = getattr(AIRecommendation, "source", None)

    if status_field is not None:
        try:
            qs = qs.filter(status="new")
        except Exception:
            # compatibilidad con estados legacy
            try:
                qs = qs.filter(status="active")
            except Exception:
                pass

    if source_field is not None:
        try:
            qs = qs.filter(source="merged")
        except Exception:
            pass

    return qs


def get_next_best_action() -> Optional[AIRecommendation]:
    scored = get_next_best_action_result()
    return scored.recommendation if scored else None


def get_next_best_action_result() -> Optional[NBAResult]:
    candidates = list(_base_queryset())
    if not candidates:
        return None

    scored = [score_recommendation(item) for item in candidates]
    scored.sort(
        key=lambda item: (
            item.final_score,
            item.urgency_score,
            item.confidence_score,
            item.recommendation.pk,
        ),
        reverse=True,
    )
    return scored[0]
