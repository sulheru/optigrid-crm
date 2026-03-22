from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.emailing.models import InboundEmail, OutboundEmail
from apps.emailing.services.reply_generator import generate_followup_draft_from_inbound
from apps.opportunities.models import Opportunity
from apps.opportunities.services.promote import promote_task_to_opportunity
from apps.recommendations.models import AIRecommendation
from apps.tasks.services.materialize import materialize_recommendation_as_task


def _resolve_opportunity_from_recommendation(recommendation: AIRecommendation):
    direct_opportunity = getattr(recommendation, "opportunity", None)
    if direct_opportunity is not None:
        return direct_opportunity

    scope_type = (getattr(recommendation, "scope_type", "") or "").strip().lower()
    scope_id = getattr(recommendation, "scope_id", None)

    if scope_type == "opportunity" and scope_id not in (None, ""):
        try:
            return Opportunity.objects.filter(pk=int(scope_id)).first()
        except (TypeError, ValueError):
            return None

    return None


def recommendation_list(request):
    status = request.GET.get("status", "").strip()
    recommendation_type = request.GET.get("recommendation_type", "").strip()

    qs = AIRecommendation.objects.all().order_by("-id")

    if status:
        qs = qs.filter(status=status)

    if recommendation_type:
        qs = qs.filter(recommendation_type=recommendation_type)

    recommendation_types = list(
        AIRecommendation.objects.order_by()
        .values_list("recommendation_type", flat=True)
        .distinct()
    )

    status_choices = getattr(AIRecommendation, "STATUS_CHOICES", [])
    if not status_choices:
        status_choices = [
            ("new", "New"),
            ("materialized", "Materialized"),
            ("dismissed", "Dismissed"),
            ("executed", "Executed"),
        ]

    context = {
        "recommendations": qs[:200],
        "status_choices": status_choices,
        "selected_status": status,
        "selected_recommendation_type": recommendation_type,
        "recommendation_types": recommendation_types,
    }
    return render(request, "recommendations/list.html", context)


@require_POST
def recommendation_create_task(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    materialize_recommendation_as_task(recommendation)
    return redirect("/recommendations/")


@require_POST
def recommendation_dismiss(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    if recommendation.status == "dismissed":
        return redirect("/recommendations/")

    recommendation.status = "dismissed"
    recommendation.save(update_fields=["status"])
    return redirect("/recommendations/")


@require_POST
def recommendation_promote_opportunity(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    existing = Opportunity.objects.filter(source_recommendation=recommendation).first()
    if existing:
        return redirect("/opportunities/prioritized/")

    task = materialize_recommendation_as_task(recommendation)
    opportunity = promote_task_to_opportunity(task)

    if hasattr(opportunity, "source_recommendation_id") and not opportunity.source_recommendation_id:
        opportunity.source_recommendation = recommendation
        opportunity.save(update_fields=["source_recommendation", "updated_at"])

    return redirect("/opportunities/prioritized/")


@require_POST
def execute_followup(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    opportunity = _resolve_opportunity_from_recommendation(recommendation)

    inbound = None
    if opportunity is not None:
        inbound = (
            InboundEmail.objects.filter(opportunity=opportunity)
            .order_by("-received_at", "-created_at")
            .first()
        )

    if inbound:
        generate_followup_draft_from_inbound(inbound)
    elif opportunity is not None:
        opportunity_name = (
            getattr(opportunity, "title", None)
            or getattr(opportunity, "company_name", None)
            or "Opportunity"
        )
        OutboundEmail.objects.create(
            opportunity=opportunity,
            email_type=OutboundEmail.TYPE_FOLLOWUP,
            subject=f"Follow-up — {opportunity_name}",
            body="Just checking in regarding our previous conversation.",
        )

    return redirect("/outbox/?type=followup")
