from apps.recommendations.models import AIRecommendation
from apps.recommendations.services.factory import create_recommendation


def recommend_next_action(scope_type, scope_id, recommendation_type, recommendation_text, confidence):
    return create_recommendation(
        scope_type=scope_type,
        scope_id=scope_id,
        recommendation_type=recommendation_type,
        recommendation_text=recommendation_text,
        confidence=confidence,
        source=AIRecommendation.SOURCE_RULES,
        status=AIRecommendation.STATUS_NEW,
    )
