import json

from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

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



OPPORTUNITY_STAGE_CHOICES = ["new", "qualified", "proposal", "won", "lost"]

OPPORTUNITY_STAGE_TRANSITIONS = {
    "new": ["qualified"],
    "qualified": ["proposal", "lost"],
    "proposal": ["won", "lost"],
    "won": [],
    "lost": [],
}

OPPORTUNITY_ALLOWED_SORTS = {
    "updated_at": "-updated_at",
    "-updated_at": "-updated_at",
    "created_at": "created_at",
    "-created_at": "-created_at",
    "estimated_value": "estimated_value",
    "-estimated_value": "-estimated_value",
    "confidence": "confidence",
    "-confidence": "-confidence",
    "title": "title",
    "-title": "-title",
}


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


def tasks_list_view(request):
    tasks = CRMTask.objects.all().order_by("-created_at", "-id")
    return render(request, "tasks/list.html", {
        "tasks": tasks,
    })


def opportunities_list_view(request):
    opportunities_qs = Opportunity.objects.all()

    stage = (request.GET.get("stage") or "").strip()
    requested_sort = (request.GET.get("sort") or "-updated_at").strip()
    sort = OPPORTUNITY_ALLOWED_SORTS.get(requested_sort, "-updated_at")

    if stage and stage in OPPORTUNITY_STAGE_CHOICES:
        opportunities_qs = opportunities_qs.filter(stage=stage)

    if sort in ("estimated_value", "-estimated_value"):
        descending = sort.startswith("-")
        opportunities_qs = opportunities_qs.order_by(
            F("estimated_value").desc(nulls_last=True) if descending else F("estimated_value").asc(nulls_last=True),
            F("updated_at").desc(nulls_last=True),
        )
    elif sort in ("confidence", "-confidence"):
        descending = sort.startswith("-")
        opportunities_qs = opportunities_qs.order_by(
            F("confidence").desc(nulls_last=True) if descending else F("confidence").asc(nulls_last=True),
            F("updated_at").desc(nulls_last=True),
        )
    else:
        opportunities_qs = opportunities_qs.order_by(sort)

    opportunities = list(opportunities_qs)

    for opportunity in opportunities:
        opportunity.available_next_stages = OPPORTUNITY_STAGE_TRANSITIONS.get(opportunity.stage, [])

    stage_counts = {stage_name: 0 for stage_name in OPPORTUNITY_STAGE_CHOICES}
    total_estimated_value = 0
    estimated_value_count = 0
    confidence_total = 0.0
    confidence_count = 0

    for opportunity in opportunities:
        if opportunity.stage in stage_counts:
            stage_counts[opportunity.stage] += 1

        if opportunity.estimated_value is not None:
            total_estimated_value += opportunity.estimated_value
            estimated_value_count += 1

        if opportunity.confidence is not None:
            confidence_total += float(opportunity.confidence)
            confidence_count += 1

    average_confidence = round(confidence_total / confidence_count, 2) if confidence_count else None

    opportunity_columns = []
    if not stage:
        for stage_name in OPPORTUNITY_STAGE_CHOICES:
            items = [op for op in opportunities if op.stage == stage_name]
            opportunity_columns.append(
                {
                    "key": stage_name,
                    "label": stage_name.capitalize(),
                    "items": items,
                    "count": len(items),
                }
            )

    return render(
        request,
        "opportunities/list.html",
        {
            "opportunities": opportunities,
            "opportunity_columns": opportunity_columns,
            "current_stage": stage,
            "current_sort": requested_sort if requested_sort in OPPORTUNITY_ALLOWED_SORTS else "-updated_at",
            "stage_choices": OPPORTUNITY_STAGE_CHOICES,
            "total_results": len(opportunities),
            "metrics": {
                "total_opportunities": len(opportunities),
                "total_estimated_value": total_estimated_value,
                "estimated_value_count": estimated_value_count,
                "average_confidence": average_confidence,
                "new_count": stage_counts["new"],
                "qualified_count": stage_counts["qualified"],
                "proposal_count": stage_counts["proposal"],
                "won_count": stage_counts["won"],
                "lost_count": stage_counts["lost"],
            },
        },
    )
def _build_opportunity_payload_from_recommendation(recommendation):
    text = (recommendation.recommendation_text or "").strip()
    title = text[:255] if text else "Opportunity detected from recommendation"

    return {
        "title": title,
        "summary": text or title,
        "stage": "new",
        "confidence": getattr(recommendation, "confidence", 0.0) or 0.0,
        "company_name": "",
    }


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
def recommendation_promote_opportunity_view(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    allowed_types = {
        "opportunity_review",
        "prepare_proposal",
        "schedule_call",
        "pricing_strategy",
        "qualification",
    }

    if recommendation.recommendation_type not in allowed_types:
        return redirect("recommendations")

    if recommendation.status == "dismissed":
        return redirect("recommendations")

    payload = _build_opportunity_payload_from_recommendation(recommendation)

    # Dedupe preferente por recommendation origen.
    opportunity = Opportunity.objects.filter(
        source_recommendation=recommendation,
    ).order_by("-id").first()

    # Fallback histórico para oportunidades antiguas sin linkage explícito.
    if opportunity is None:
        opportunity = Opportunity.objects.filter(
            title=payload["title"],
            summary=payload["summary"],
        ).order_by("-id").first()

    if opportunity is None:
        opportunity = Opportunity.objects.create(
            source_recommendation=recommendation,
            title=payload["title"],
            summary=payload["summary"],
            stage=payload["stage"],
            confidence=payload["confidence"],
            company_name=payload["company_name"],
        )
    else:
        updated_fields = []

        if opportunity.source_recommendation_id is None:
            opportunity.source_recommendation = recommendation
            updated_fields.append("source_recommendation")

        if updated_fields:
            opportunity.save(update_fields=updated_fields)

    if recommendation.status != "executed":
        recommendation.status = "executed"
        recommendation.save(update_fields=["status"])

    return redirect("opportunities")


@require_POST


def opportunity_set_stage_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    opportunity = get_object_or_404(Opportunity, pk=pk)
    target_stage = (request.POST.get("stage") or "").strip()

    if target_stage not in OPPORTUNITY_STAGE_CHOICES:
        messages.error(request, "Stage inválido.")
        return redirect("opportunities")

    allowed_targets = OPPORTUNITY_STAGE_TRANSITIONS.get(opportunity.stage, [])
    if target_stage not in allowed_targets:
        messages.error(
            request,
            f"No se permite transición de '{opportunity.stage}' a '{target_stage}'.",
        )
        return redirect("opportunities")

    previous_stage = opportunity.stage
    opportunity.stage = target_stage
    opportunity.save(update_fields=["stage", "updated_at"])

    messages.success(
        request,
        f"Opportunity #{opportunity.pk} movida de '{previous_stage}' a '{target_stage}'.",
    )

    next_url = (request.POST.get("next") or "").strip()
    if next_url:
        return redirect(next_url)

    return redirect("opportunities")


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
