from __future__ import annotations

from django.apps import apps
from django.db.models import Count
from django.shortcuts import get_object_or_404, render


def _model(app_label: str, model_name: str):
    return apps.get_model(app_label, model_name)


def _field_names(model) -> set[str]:
    return {f.name for f in model._meta.get_fields()}


def _date_field_for(model) -> str:
    candidates = [
        "received_at",
        "sent_at",
        "created_at",
        "updated_at",
        "timestamp",
        "date",
    ]
    fields = _field_names(model)
    for name in candidates:
        if name in fields:
            return name
    return "pk"


def _source_filter(model, email_obj):
    fields = _field_names(model)

    if "source_type" in fields and "source_id" in fields:
        return {"source_type": "email_message", "source_id": email_obj.pk}

    if "scope_type" in fields and "scope_id" in fields:
        return {"scope_type": "email_message", "scope_id": email_obj.pk}

    if "email_message" in fields:
        return {"email_message": email_obj}

    if "message" in fields:
        return {"message": email_obj}

    return None


def email_list_view(request):
    EmailMessage = _model("emailing", "EmailMessage")
    date_field = _date_field_for(EmailMessage)

    emails = EmailMessage.objects.all().order_by(f"-{date_field}")[:50]

    return render(
        request,
        "emailing/email_list.html",
        {
            "emails": emails,
        },
    )


def email_detail_view(request, email_id: int):
    EmailMessage = _model("emailing", "EmailMessage")
    FactRecord = _model("facts", "FactRecord")
    InferenceRecord = _model("inferences", "InferenceRecord")
    CRMUpdateProposal = _model("updates", "CRMUpdateProposal")
    AIRecommendation = _model("recommendations", "AIRecommendation")
    Event = _model("events", "Event")

    email_obj = get_object_or_404(EmailMessage, pk=email_id)

    facts_filter = _source_filter(FactRecord, email_obj)
    inferences_filter = _source_filter(InferenceRecord, email_obj)
    proposals_filter = _source_filter(CRMUpdateProposal, email_obj)
    recommendations_filter = _source_filter(AIRecommendation, email_obj)

    facts = FactRecord.objects.filter(**facts_filter).order_by("pk") if facts_filter else FactRecord.objects.none()
    inferences = InferenceRecord.objects.filter(**inferences_filter).order_by("pk") if inferences_filter else InferenceRecord.objects.none()
    proposals = CRMUpdateProposal.objects.filter(**proposals_filter).order_by("pk") if proposals_filter else CRMUpdateProposal.objects.none()

    if recommendations_filter:
        recommendations = AIRecommendation.objects.filter(**recommendations_filter).order_by("pk")
    else:
        recommendation_fields = _field_names(AIRecommendation)
        if "scope_type" in recommendation_fields and "scope_id" in recommendation_fields:
            inference_ids = list(inferences.values_list("pk", flat=True))
            recommendations = AIRecommendation.objects.filter(
                scope_type="inference_record",
                scope_id__in=inference_ids,
            ).order_by("pk")
        else:
            recommendations = AIRecommendation.objects.none()

    event_fields = _field_names(Event)
    if "aggregate_type" in event_fields and "aggregate_id" in event_fields:
        events = Event.objects.filter(
            aggregate_type__in=[
                "email_message",
                "fact_record",
                "inference_record",
                "crm_update_proposal",
                "ai_recommendation",
            ]
        ).order_by("-pk")[:100]
    else:
        events = Event.objects.all().order_by("-pk")[:100]

    return render(
        request,
        "emailing/email_detail.html",
        {
            "email": email_obj,
            "facts": facts,
            "inferences": inferences,
            "proposals": proposals,
            "recommendations": recommendations,
            "events": events,
        },
    )
