import json

from django.shortcuts import get_object_or_404, render

from apps.emailing.models import EmailMessage
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from apps.recommendations.models import AIRecommendation

from apps.tasks.models import CRMTask
from apps.opportunities.models import Opportunity

def _pretty_json(value):
    if value is None:
        return "{}"
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(value)


def _extract_payload(obj):
    for attr in ("value", "payload", "proposed_payload"):
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return None




def _map_recommendation_type_to_task_type(recommendation_type):
    value = (recommendation_type or "").strip()

    mapping = {
        "reply_strategy": "reply_email",
        "followup": "follow_up",
        "schedule_call": "schedule_call",
        "prepare_proposal": "prepare_proposal",
        "qualification": "review_manually",
        "opportunity_review": "review_manually",
        "pricing_strategy": "review_manually",
        "timing_strategy": "review_manually",
        "contact_strategy": "review_manually",
        "next_action": "review_manually",
        "hold": "review_manually",
    }

    return mapping.get(value, "review_manually")

def _count_pipeline_objects_for_email(email):
    facts_qs = FactRecord.objects.filter(
        source_type="email_message",
        source_id=email.id,
    )

    inferences_qs = InferenceRecord.objects.filter(
        source_type="email_message",
        source_id=email.id,
    )

    inference_ids = list(inferences_qs.values_list("id", flat=True))

    proposals_qs = CRMUpdateProposal.objects.filter(
        target_entity_type="inference_record",
        target_entity_id__in=inference_ids,
    )

    recommendations_qs = AIRecommendation.objects.filter(
        scope_type="inference",
        scope_id__in=inference_ids,
    )

    return {
        "facts_count": facts_qs.count(),
        "inferences_count": inferences_qs.count(),
        "proposals_count": proposals_qs.count(),
        "recommendations_count": recommendations_qs.count(),
    }


def dashboard_view(request):
    total_emails = EmailMessage.objects.count()
    total_recommendations = AIRecommendation.objects.count()
    total_proposals = CRMUpdateProposal.objects.count()

    pending_proposals = CRMUpdateProposal.objects.filter(
        proposal_status="pending"
    ).count()

    recent_emails = list(
        EmailMessage.objects.all().order_by("-sent_at", "-created_at", "-id")[:8]
    )

    for email in recent_emails:
        counts = _count_pipeline_objects_for_email(email)
        email.facts_count = counts["facts_count"]
        email.inferences_count = counts["inferences_count"]
        email.proposals_count = counts["proposals_count"]
        email.recommendations_count = counts["recommendations_count"]

    recent_proposals = CRMUpdateProposal.objects.all().order_by("-created_at", "-id")[:8]
    recent_recommendations = AIRecommendation.objects.all().order_by("-created_at", "-id")[:8]

    context = {
        "total_emails": total_emails,
        "total_recommendations": total_recommendations,
        "total_proposals": total_proposals,
        "pending_proposals": pending_proposals,
        "recent_emails": recent_emails,
        "recent_proposals": recent_proposals,
        "recent_recommendations": recent_recommendations,
    }
    return render(request, "dashboard/home.html", context)


def email_list_view(request):
    emails = list(
        EmailMessage.objects.all().order_by("-sent_at", "-created_at", "-id")
    )

    for email in emails:
        counts = _count_pipeline_objects_for_email(email)
        email.facts_count = counts["facts_count"]
        email.inferences_count = counts["inferences_count"]
        email.proposals_count = counts["proposals_count"]
        email.recommendations_count = counts["recommendations_count"]

    context = {
        "emails": emails,
    }
    return render(request, "emailing/email_list.html", context)


def email_detail_view(request, pk):
    email = get_object_or_404(EmailMessage, pk=pk)

    facts = list(
        FactRecord.objects.filter(
            source_type="email_message",
            source_id=email.id,
        ).order_by("id")
    )

    inferences = list(
        InferenceRecord.objects.filter(
            source_type="email_message",
            source_id=email.id,
        ).order_by("id")
    )

    inference_ids = [obj.id for obj in inferences]

    proposals = list(
        CRMUpdateProposal.objects.filter(
            target_entity_type="inference_record",
            target_entity_id__in=inference_ids,
        ).order_by("id")
    )

    recommendations = list(
        AIRecommendation.objects.filter(
            scope_type="inference",
            scope_id__in=inference_ids,
        ).order_by("id")
    )

    for obj in facts:
        obj.display_payload = _pretty_json(_extract_payload(obj))

    for obj in inferences:
        obj.display_payload = _pretty_json(_extract_payload(obj))

    for obj in proposals:
        obj.display_payload = _pretty_json(_extract_payload(obj))

    context = {
        "email": email,
        "facts": facts,
        "inferences": inferences,
        "proposals": proposals,
        "recommendations": recommendations,
    }
    return render(request, "emailing/email_detail.html", context)


def recommendations_list_view(request):
    recommendations = AIRecommendation.objects.all().order_by("-created_at", "-id")

    status = (request.GET.get("status") or "").strip()
    recommendation_type = (request.GET.get("recommendation_type") or "").strip()

    if status:
        recommendations = recommendations.filter(status=status)

    if recommendation_type:
        recommendations = recommendations.filter(recommendation_type=recommendation_type)

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


def tasks_list_view(request):
    tasks = CRMTask.objects.all().order_by("-created_at", "-id")
    return render(request, "tasks/list.html", {
        "tasks": tasks,
    })


def opportunities_list_view(request):
    opportunities = Opportunity.objects.all().order_by("-created_at", "-id")
    return render(request, "opportunities/list.html", {
        "opportunities": opportunities,
    })

from django.shortcuts import redirect
from django.views.decorators.http import require_POST


@require_POST
def recommendation_create_task_view(request, pk):

    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    task_type = _map_recommendation_type_to_task_type(recommendation.recommendation_type)

    task, created = CRMTask.objects.get_or_create(
        source_recommendation=recommendation,
        defaults={
            "title": recommendation.recommendation_text[:200],
            "description": recommendation.recommendation_text,
            "task_type": task_type,
            "status": "open",
            "priority": "normal",
        },
    )

    updated_fields = []

    if task.task_type != task_type:
        task.task_type = task_type
        updated_fields.append("task_type")

    if not task.description and recommendation.recommendation_text:
        task.description = recommendation.recommendation_text
        updated_fields.append("description")

    if updated_fields:
        task.save(update_fields=updated_fields)

    if recommendation.status != "materialized":
        recommendation.status = "materialized"
        recommendation.save(update_fields=["status"])

    return redirect("recommendations")


@require_POST
def recommendation_dismiss_view(request, pk):

    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    if recommendation.status not in ["dismissed", "executed"]:
        recommendation.status = "dismissed"
        recommendation.save(update_fields=["status"])

    return redirect("recommendations")


@require_POST
def task_set_status_view(request, pk):
    task = get_object_or_404(CRMTask, pk=pk)

    new_status = (request.POST.get("status") or "").strip()
    allowed_statuses = {"open", "in_progress", "done", "dismissed"}

    if new_status in allowed_statuses and task.status != new_status:
        task.status = new_status
        task.save(update_fields=["status"])

    return redirect("tasks")

