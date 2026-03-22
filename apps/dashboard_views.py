# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/dashboard_views.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.shortcuts import render

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
        AIRecommendation.objects.filter(status="new")
    )

    scored = []
    for recommendation in recommendations:
        recommendation.priority_score = compute_priority_score(recommendation)
        scored.append(recommendation)

    scored.sort(key=lambda x: x.priority_score, reverse=True)

    top_actions = scored[:5]

    high_urgency = [r for r in scored if r.priority_score >= 70][:5]
    medium_urgency = [r for r in scored if 40 <= r.priority_score < 70][:5]
    low_urgency = [r for r in scored if r.priority_score < 40][:5]

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
        "urgency_high": high_urgency,
        "urgency_medium": medium_urgency,
        "urgency_low": low_urgency,
        "recent_activity": recent_activity,
    }

    return render(request, "dashboard/home.html", context)
