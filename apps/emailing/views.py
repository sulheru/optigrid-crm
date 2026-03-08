import json

from django.shortcuts import get_object_or_404, render

from apps.emailing.models import EmailMessage
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from apps.recommendations.models import AIRecommendation


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
    """
    Devuelve una representación segura para mostrar en template,
    sin depender de que todos los modelos usen el mismo nombre de campo.
    """
    for attr in ("value", "payload", "proposed_payload"):
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return None


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
