# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/views.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.ui_semantics import build_available_actions, get_recommendation_ui
from apps.emailing.models import InboundEmail, OutboundEmail
from apps.emailing.services.reply_generator import generate_followup_draft_from_inbound
from apps.opportunities.models import Opportunity
from apps.opportunities.services.promote import promote_task_to_opportunity
from apps.recommendations.models import AIRecommendation
from apps.tasks.services.materialize import materialize_recommendation_as_task


RECOMMENDATIONS_LIST_PATH = "/recommendations/"
OPPORTUNITIES_PRIORITIZED_PATH = "/opportunities/prioritized/"
OUTBOX_FOLLOWUP_PATH = "/outbox/?type=followup"
OUTBOX_FIRST_CONTACT_PATH = "/outbox/?type=first_contact"

DEFAULT_STATUS_CHOICES = [
    (AIRecommendation.STATUS_NEW, "New"),
    (AIRecommendation.STATUS_MATERIALIZED, "Materialized"),
    (AIRecommendation.STATUS_DISMISSED, "Dismissed"),
    (AIRecommendation.STATUS_EXECUTED, "Executed"),
]


def _normalized_text(value):
    return (value or "").strip().lower()


def _recommendation_list_redirect():
    return redirect(RECOMMENDATIONS_LIST_PATH)


def _resolve_opportunity_from_recommendation(recommendation: AIRecommendation):
    direct_opportunity = getattr(recommendation, "opportunity", None)
    if direct_opportunity is not None:
        return direct_opportunity

    scope_type = _normalized_text(getattr(recommendation, "scope_type", ""))
    scope_id = getattr(recommendation, "scope_id", None)

    if scope_type == "opportunity" and scope_id not in (None, ""):
        try:
            return Opportunity.objects.filter(pk=int(scope_id)).first()
        except (TypeError, ValueError):
            return None

    return None


def _find_reusable_followup_for_inbound(inbound: InboundEmail):
    if inbound is None:
        return None

    return (
        OutboundEmail.objects.filter(
            source_inbound=inbound,
            email_type=OutboundEmail.TYPE_FOLLOWUP,
            status__in=[
                OutboundEmail.STATUS_DRAFT,
                OutboundEmail.STATUS_APPROVED,
            ],
        )
        .order_by("-created_at")
        .first()
    )


def _find_reusable_followup_for_opportunity(opportunity: Opportunity):
    if opportunity is None:
        return None

    return (
        OutboundEmail.objects.filter(
            opportunity=opportunity,
            source_inbound__isnull=True,
            email_type=OutboundEmail.TYPE_FOLLOWUP,
            status__in=[
                OutboundEmail.STATUS_DRAFT,
                OutboundEmail.STATUS_APPROVED,
            ],
        )
        .order_by("-created_at")
        .first()
    )


def _build_manual_followup_draft(opportunity: Opportunity):
    opportunity_name = (
        getattr(opportunity, "title", None)
        or getattr(opportunity, "company_name", None)
        or "Opportunity"
    )

    return OutboundEmail.objects.create(
        opportunity=opportunity,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
        subject=f"Follow-up — {opportunity_name}",
        body="Just checking in regarding our previous conversation.",
        status=OutboundEmail.STATUS_DRAFT,
    )


def _find_reusable_first_contact_for_opportunity(opportunity: Opportunity):
    if opportunity is None:
        return None

    return (
        OutboundEmail.objects.filter(
            opportunity=opportunity,
            source_inbound__isnull=True,
            email_type=OutboundEmail.TYPE_FIRST_CONTACT,
            status__in=[
                OutboundEmail.STATUS_DRAFT,
                OutboundEmail.STATUS_APPROVED,
            ],
        )
        .order_by("-created_at")
        .first()
    )


def _build_first_contact_draft(opportunity: Opportunity):
    opportunity_name = (
        getattr(opportunity, "title", None)
        or getattr(opportunity, "company_name", None)
        or "Opportunity"
    )

    company_name = getattr(opportunity, "company_name", "") or opportunity_name

    subject = f"Intro — {company_name}"
    body = (
        f"Hi {company_name} team,\n\n"
        "I wanted to reach out briefly to introduce myself and explore whether "
        "there could be a fit for a conversation.\n\n"
        "If useful, I can share a short overview and suggest next steps.\n\n"
        "Best regards,"
    )

    return OutboundEmail.objects.create(
        opportunity=opportunity,
        email_type=OutboundEmail.TYPE_FIRST_CONTACT,
        subject=subject,
        body=body,
        status=OutboundEmail.STATUS_DRAFT,
    )


def _mark_recommendation_executed(recommendation: AIRecommendation):
    if recommendation.status == AIRecommendation.STATUS_EXECUTED:
        return

    recommendation.status = AIRecommendation.STATUS_EXECUTED
    recommendation.save(update_fields=["status"])


def _get_status_choices():
    status_choices = getattr(AIRecommendation, "STATUS_CHOICES", None)
    return status_choices or DEFAULT_STATUS_CHOICES


def _get_recommendation_types():
    values = (
        AIRecommendation.objects.order_by()
        .values_list("recommendation_type", flat=True)
        .distinct()
    )
    return [value for value in values if value]


def _decorate_recommendation_for_ui(recommendation: AIRecommendation):
    ui_config = get_recommendation_ui(recommendation.recommendation_type)
    recommendation.ui_icon = ui_config["icon"]
    recommendation.ui_color = ui_config["color"]
    recommendation.available_actions = build_available_actions(recommendation)
    return recommendation


def recommendation_list(request):
    selected_status = request.GET.get("status", "").strip()
    selected_recommendation_type = request.GET.get("recommendation_type", "").strip()

    recommendations_qs = AIRecommendation.objects.all().order_by("-id")

    if selected_status:
        recommendations_qs = recommendations_qs.filter(status=selected_status)

    if selected_recommendation_type:
        recommendations_qs = recommendations_qs.filter(
            recommendation_type=selected_recommendation_type
        )

    recommendations = [
        _decorate_recommendation_for_ui(recommendation)
        for recommendation in recommendations_qs[:200]
    ]

    context = {
        "recommendations": recommendations,
        "status_choices": _get_status_choices(),
        "selected_status": selected_status,
        "selected_recommendation_type": selected_recommendation_type,
        "recommendation_types": _get_recommendation_types(),
    }
    return render(request, "recommendations/list.html", context)


@require_POST
def recommendation_create_task(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    materialize_recommendation_as_task(recommendation)
    return _recommendation_list_redirect()


@require_POST
def recommendation_dismiss(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    if recommendation.status == AIRecommendation.STATUS_DISMISSED:
        return _recommendation_list_redirect()

    recommendation.status = AIRecommendation.STATUS_DISMISSED
    recommendation.save(update_fields=["status"])
    return _recommendation_list_redirect()


@require_POST
def recommendation_promote_opportunity(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    existing = Opportunity.objects.filter(source_recommendation=recommendation).first()
    if existing:
        return redirect(OPPORTUNITIES_PRIORITIZED_PATH)

    task = materialize_recommendation_as_task(recommendation)
    opportunity = promote_task_to_opportunity(task)

    if hasattr(opportunity, "source_recommendation_id") and not opportunity.source_recommendation_id:
        opportunity.source_recommendation = recommendation
        opportunity.save(update_fields=["source_recommendation", "updated_at"])

    return redirect(OPPORTUNITIES_PRIORITIZED_PATH)


@require_POST
def execute_followup(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    if recommendation.status == AIRecommendation.STATUS_EXECUTED:
        return redirect(OUTBOX_FOLLOWUP_PATH)

    opportunity = _resolve_opportunity_from_recommendation(recommendation)
    if opportunity is None:
        return _recommendation_list_redirect()

    inbound = (
        InboundEmail.objects.filter(opportunity=opportunity)
        .order_by("-received_at", "-created_at")
        .first()
    )

    outbound = None

    if inbound is not None:
        outbound = _find_reusable_followup_for_inbound(inbound)
        if outbound is None:
            outbound = generate_followup_draft_from_inbound(inbound)
    else:
        outbound = _find_reusable_followup_for_opportunity(opportunity)
        if outbound is None:
            outbound = _build_manual_followup_draft(opportunity)

    if outbound is not None:
        _mark_recommendation_executed(recommendation)

    return redirect(OUTBOX_FOLLOWUP_PATH)


@require_POST
def execute_contact_strategy(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    if recommendation.status == AIRecommendation.STATUS_EXECUTED:
        return redirect(OUTBOX_FIRST_CONTACT_PATH)

    opportunity = _resolve_opportunity_from_recommendation(recommendation)
    if opportunity is None:
        return _recommendation_list_redirect()

    outbound = _find_reusable_first_contact_for_opportunity(opportunity)
    if outbound is None:
        outbound = _build_first_contact_draft(opportunity)

    if outbound is not None:
        _mark_recommendation_executed(recommendation)

    return redirect(OUTBOX_FIRST_CONTACT_PATH)


@require_POST
def execute_reply_strategy(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    if recommendation.status == AIRecommendation.STATUS_EXECUTED:
        return redirect(OUTBOX_FOLLOWUP_PATH)

    opportunity = _resolve_opportunity_from_recommendation(recommendation)
    if opportunity is None:
        return _recommendation_list_redirect()

    inbound = (
        InboundEmail.objects.filter(opportunity=opportunity)
        .order_by("-received_at", "-created_at")
        .first()
    )
    if inbound is None:
        return _recommendation_list_redirect()

    outbound = _find_reusable_followup_for_inbound(inbound)
    if outbound is None:
        outbound = generate_followup_draft_from_inbound(inbound)

    if outbound is not None:
        _mark_recommendation_executed(recommendation)

    return redirect(OUTBOX_FOLLOWUP_PATH)


@require_POST
def execute_recommendation(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    recommendation_type = _normalized_text(recommendation.recommendation_type)

    if recommendation_type == "followup":
        return execute_followup(request, pk)

    if recommendation_type == "contact_strategy":
        return execute_contact_strategy(request, pk)

    if recommendation_type == "reply_strategy":
        return execute_reply_strategy(request, pk)

    return _recommendation_list_redirect()
