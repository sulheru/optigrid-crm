from __future__ import annotations

from apps.core.runtime_settings import (
    get_runtime_float_setting,
    get_runtime_list_setting,
    get_runtime_str_setting,
)
from apps.recommendations.models import AIRecommendation


ALLOWED_RECOMMENDATION_TYPES = {
    "followup",
    "contact_strategy",
    "reply_strategy",
    "opportunity_review",
    "pricing_strategy",
    "advance_opportunity",
    "mark_lost",
}

RECOMMENDATION_TYPE_ALIASES = {
    "follow_up": "followup",
    "follow-up": "followup",
    "follow up": "followup",
    "followup_later": "followup",
    "follow_up_later": "followup",
    "contact": "contact_strategy",
    "contact_strategy_review": "contact_strategy",
    "reply": "reply_strategy",
    "reply_with_scope_clarification": "reply_strategy",
    "opportunity": "opportunity_review",
    "review_opportunity": "opportunity_review",
    "pricing": "pricing_strategy",
    "pricing_review": "pricing_strategy",
    "advance": "advance_opportunity",
    "advance_stage": "advance_opportunity",
    "lost": "mark_lost",
    "mark_as_lost": "mark_lost",
}


def normalize_recommendation_type(value: str) -> str:
    normalized = (value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return RECOMMENDATION_TYPE_ALIASES.get(normalized, normalized)


def is_allowed_recommendation_type(value: str) -> bool:
    return normalize_recommendation_type(value) in ALLOWED_RECOMMENDATION_TYPES


def normalize_confidence(value, default: float = 0.7) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return default

    if confidence < 0.0:
        return 0.0
    if confidence > 1.0:
        return 1.0
    return confidence


def build_recommendation_text(rec: dict) -> str:
    text = (rec.get("text") or "").strip()
    if text:
        return text

    value = rec.get("value") or {}
    if isinstance(value, dict):
        summary = (value.get("reason") or value.get("summary") or "").strip()
        if summary:
            return summary

    return ""


def get_llm_output_mode() -> str:
    return get_runtime_str_setting("LLM_OUTPUT_MODE", "hybrid").strip().lower() or "hybrid"


def get_llm_min_confidence() -> float:
    return get_runtime_float_setting("LLM_MIN_CONFIDENCE", 0.7)


def get_allowed_recommendation_types() -> set[str]:
    configured = get_runtime_list_setting(
        "LLM_ALLOWED_RECOMMENDATION_TYPES",
        [
            "followup",
            "contact_strategy",
            "reply_strategy",
            "opportunity_review",
            "pricing_strategy",
            "advance_opportunity",
            "mark_lost",
        ],
    )

    normalized = {
        normalize_recommendation_type(value)
        for value in configured
        if isinstance(value, str) and value.strip()
    }
    return normalized & ALLOWED_RECOMMENDATION_TYPES


def should_accept_llm_recommendation(rec_type: str, confidence: float) -> bool:
    mode = get_llm_output_mode()

    if mode == "inference_only":
        return False

    allowed_types = get_allowed_recommendation_types()
    if rec_type not in allowed_types:
        return False

    min_confidence = get_llm_min_confidence()
    if confidence < min_confidence:
        return False

    return True


def create_recommendations_from_llm_output(
    *,
    scope_type: str,
    scope_id: int,
    llm_result: dict,
):
    created = []

    for rec in llm_result.get("recommendations", []):
        rec_type = normalize_recommendation_type(rec.get("type", ""))
        rec_text = build_recommendation_text(rec)
        confidence = normalize_confidence(rec.get("confidence", 0.7))

        if not rec_type or rec_type not in ALLOWED_RECOMMENDATION_TYPES:
            continue

        if not rec_text:
            continue

        if not should_accept_llm_recommendation(rec_type, confidence):
            continue

        existing = AIRecommendation.objects.filter(
            scope_type=scope_type,
            scope_id=scope_id,
            recommendation_type=rec_type,
            recommendation_text=rec_text,
        ).first()
        if existing:
            continue

        obj = AIRecommendation.objects.create(
            scope_type=scope_type,
            scope_id=scope_id,
            recommendation_type=rec_type,
            recommendation_text=rec_text,
            confidence=confidence,
            status="new",
        ,
            source="llm")
        created.append(obj)

    return created
