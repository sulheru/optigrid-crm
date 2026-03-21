from django.shortcuts import render

from apps.emailing.models import InboundEmail, OutboundEmail
from apps.opportunities.models import Opportunity
from apps.recommendations.models import AIRecommendation


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

    top_actions_raw = list(
        AIRecommendation.objects.order_by("-confidence", "-id")[:5]
    )

    top_actions = []
    for recommendation in top_actions_raw:
        recommendation_type = recommendation.recommendation_type or "recommendation"

        if recommendation_type == "followup":
            primary_action_label = "Send Follow-up"
            primary_action_url = f"/recommendations/{recommendation.id}/create-task/"
            action_enabled = True

        elif recommendation_type == "reply_strategy":
            primary_action_label = "Prepare Reply"
            primary_action_url = f"/recommendations/{recommendation.id}/create-task/"
            action_enabled = True

        elif recommendation_type == "contact_strategy":
            primary_action_label = "Start Contact"
            primary_action_url = f"/recommendations/{recommendation.id}/create-task/"
            action_enabled = True

        elif recommendation_type in ["next_action", "qualification"]:
            primary_action_label = "Create Task"
            primary_action_url = f"/recommendations/{recommendation.id}/create-task/"
            action_enabled = True

        elif recommendation_type == "opportunity_review":
            primary_action_label = "Promote to Opportunity"
            primary_action_url = f"/recommendations/{recommendation.id}/promote-opportunity/"
            action_enabled = True

        elif recommendation_type in ["pricing_strategy", "timing_strategy"]:
            primary_action_label = "Review Strategy"
            primary_action_url = f"/recommendations/{recommendation.id}/create-task/"
            action_enabled = True

        elif recommendation_type == "risk_flag":
            primary_action_label = "Review Risk"
            primary_action_url = f"/recommendations/{recommendation.id}/create-task/"
            action_enabled = True

        elif recommendation_type == "hold":
            primary_action_label = "No Action"
            primary_action_url = ""
            action_enabled = False

        else:
            primary_action_label = "Create Task"
            primary_action_url = f"/recommendations/{recommendation.id}/create-task/"
            action_enabled = True

        top_actions.append(
            {
                "id": recommendation.id,
                "recommendation_type": recommendation_type,
                "status": recommendation.status or "—",
                "confidence": recommendation.confidence if recommendation.confidence is not None else "—",
                "recommendation_text": recommendation.recommendation_text,
                "inspect_url": "/recommendations/",
                "primary_action_label": primary_action_label,
                "primary_action_url": primary_action_url,
                "action_enabled": action_enabled,
                "dismiss_url": f"/recommendations/{recommendation.id}/dismiss/",
            }
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
    }
    return render(request, "dashboard/home.html", context)
