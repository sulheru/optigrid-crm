from django.http import JsonResponse

from apps.recommendations.models import AIRecommendation
from apps.recommendations.nba import get_next_best_action_explained, get_score_breakdown


def simulate_recommendation(request, rec_id):
    try:
        rec = AIRecommendation.objects.get(id=rec_id)
    except AIRecommendation.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    breakdown = get_score_breakdown(rec)
    active_recommendations = AIRecommendation.objects.filter(status="new")
    nba_result = get_next_best_action_explained(active_recommendations)

    selected_as_best_action = bool(
        nba_result and nba_result.recommendation.id == rec.id
    )

    alternatives = []
    why_not_others = []
    if nba_result:
        alternatives = [
            {
                "id": alt.recommendation.id,
                "type": alt.recommendation.recommendation_type,
                "score": alt.breakdown.total_score,
                "gap_vs_winner": alt.gap_vs_winner,
                "summary": alt.summary,
            }
            for alt in nba_result.alternatives
        ]
        why_not_others = nba_result.why_not_others

    return JsonResponse(
        {
            "id": rec.id,
            "type": rec.recommendation_type,
            "selected_as_best_action": selected_as_best_action,
            "score": breakdown.total_score,
            "breakdown": {
                "priority_raw": breakdown.priority_raw,
                "priority_component": breakdown.priority_component,
                "confidence_raw": breakdown.confidence_raw,
                "confidence_component": breakdown.confidence_component,
                "urgency_raw": breakdown.urgency_raw,
                "urgency_component": breakdown.urgency_component,
                "type_weight_raw": breakdown.type_weight_raw,
                "type_weight_component": breakdown.type_weight_component,
            },
            "winner": {
                "id": nba_result.recommendation.id,
                "type": nba_result.recommendation.recommendation_type,
                "score": nba_result.breakdown.total_score,
                "why_selected": nba_result.why_selected,
            }
            if nba_result
            else None,
            "why_not_others": why_not_others,
            "alternatives": alternatives,
        }
    )
