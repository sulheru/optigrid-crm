# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/patch_views_recommendations.py
from django.shortcuts import render
from apps.recommendations.models import AIRecommendation

def recommendations_list_view(request):

    qs = AIRecommendation.objects.all()

    status = (request.GET.get("status") or "").strip()
    recommendation_type = (request.GET.get("recommendation_type") or "").strip()

    if status:
        qs = qs.filter(status=status)

    if recommendation_type:
        qs = qs.filter(recommendation_type=recommendation_type)

    recommendations = qs.order_by("-created_at", "-id")

    recommendation_types = (
        AIRecommendation.objects
        .order_by("recommendation_type")
        .values_list("recommendation_type", flat=True)
        .distinct()
    )

    return render(request, "recommendations/list.html", {
        "recommendations": recommendations,
        "selected_status": status,
        "selected_recommendation_type": recommendation_type,
        "status_choices": AIRecommendation.STATUS_CHOICES,
        "recommendation_types": recommendation_types,
    })
