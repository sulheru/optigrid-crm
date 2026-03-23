from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.recommendations.models import AIRecommendation
from apps.recommendations.ranking_engine import (
    rank_recommendations,
    get_next_best_action,
)
from apps.recommendations.simulation import simulate_alternative


def simulate_recommendation(request, recommendation_id):
    candidate = get_object_or_404(AIRecommendation, pk=recommendation_id)

    recs = list(
        AIRecommendation.objects.filter(status=AIRecommendation.STATUS_NEW)
    )

    ranked = rank_recommendations(recs)
    nba = get_next_best_action(ranked)

    result = simulate_alternative(candidate, nba)

    return JsonResponse({
        "candidate_id": candidate.id,
        "nba_id": getattr(nba, "id", None),
        "simulation": result,
    })
