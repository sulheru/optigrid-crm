from __future__ import annotations

from apps.recommendations.models import AIRecommendation


def create_recommendation(
    *,
    scope_type: str,
    scope_id,
    recommendation_type: str,
    recommendation_text: str,
    confidence: float,
    source: str = AIRecommendation.SOURCE_RULES,
    status: str = AIRecommendation.STATUS_NEW,
) -> AIRecommendation:
    obj = AIRecommendation.objects.create(
        scope_type=scope_type,
        scope_id=str(scope_id),
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=confidence,
        source=source,
        status=status,
    )

    print(
        f"[FLOW] Recommendation created id={obj.id} "
        f"type={obj.recommendation_type} "
        f"scope={obj.scope_type}:{obj.scope_id} "
        f"source={obj.source}"
    )
    return obj
