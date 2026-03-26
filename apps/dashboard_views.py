from django.shortcuts import render

from apps.recommendations.models import AIRecommendation
from apps.recommendations.nba import get_next_best_action_explained


def dashboard_home_view(request):
    recommendations = AIRecommendation.objects.filter(status="new")

    nba_result = get_next_best_action_explained(recommendations)
    best_action = nba_result.recommendation if nba_result else None

    context = {
        "recommendations": recommendations,
        "best_action": best_action,
        "best_action_explanation": nba_result,
        "best_action_breakdown": nba_result.breakdown if nba_result else None,
        "best_action_alternatives": nba_result.alternatives if nba_result else [],
    }

    return render(request, "dashboard/index.html", context)
