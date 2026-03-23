# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/dashboard_views.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.shortcuts import render

from apps.core.ui_semantics import (
    build_available_actions,
    get_priority_level,
    get_recommendation_ui,
)
from apps.emailing.models import InboundEmail, OutboundEmail
from apps.events.models import ActivityEvent
from apps.opportunities.models import Opportunity
from apps.recommendations.models import AIRecommendation
from apps.recommendations.priority import compute_priority_score


def dashboard_home_view(request):
    recent_inbound = list(
        InboundEmail.objects.order_by("-received_at", "-created_at")[:5]
    )
    recent_outbound = list(
        OutboundEmail.objects.select_related("opportunity").order_by("-created_at")[:5]
    )
    recent_recommendations = list(
        AIRecommendation.objects.order_by("-id")[:5]
    )
    recent_opportunities = list(
        Opportunity.objects.order_by("-updated_at", "-id")[:5]
    )

    recommendations = list(
        AIRecommendation.objects.filter(status=AIRecommendation.STATUS_NEW)
    )

    scored = []
    for recommendation in recommendations:
        recommendation.priority_score = compute_priority_score(recommendation)

        priority_level, priority_config = get_priority_level(
            recommendation.priority_score
        )
        recommendation.priority_level = priority_level
        recommendation.priority_label = priority_config["label"]
        recommendation.priority_css = priority_config["css"]
        recommendation.priority_color = priority_config["color"]

        ui_config = get_recommendation_ui(recommendation.recommendation_type)
        recommendation.ui_icon = ui_config["icon"]
        recommendation.ui_color = ui_config["color"]
        recommendation.available_actions = build_available_actions(recommendation)

        scored.append(recommendation)

    scored.sort(key=lambda x: x.priority_score, reverse=True)

    top_actions = scored[:10]
    best_action = top_actions[0] if top_actions else None

    high_urgency = [r for r in scored if r.priority_level == "high"][:5]
    medium_urgency = [r for r in scored if r.priority_level == "medium"][:5]
    low_urgency = [r for r in scored if r.priority_level == "low"][:5]

    recent_activity = list(
        ActivityEvent.objects.order_by("-created_at")[:10]
    )

    context = {
        "total_inbound_emails": InboundEmail.objects.count(),
        "total_outbound_emails": OutboundEmail.objects.count(),
        "total_recommendations": AIRecommendation.objects.count(),
        "total_opportunities": Opportunity.objects.count(),
        "recent_inbound_emails": recent_inbound,
        "recent_outbound_emails": recent_outbound,
        "recent_recommendations": recent_recommendations,
        "recent_opportunities": recent_opportunities,
        "top_actions": top_actions,
        "best_action": best_action,
        "urgency_high": high_urgency,
        "urgency_medium": medium_urgency,
        "urgency_low": low_urgency,
        "recent_activity": recent_activity,
    }

    return render(request, "dashboard/home.html", context)
