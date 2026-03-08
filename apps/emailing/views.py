from django.shortcuts import get_object_or_404, render

from apps.emailing.models import EmailMessage
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from apps.recommendations.models import AIRecommendation


EMAIL_SOURCE_TYPES = ["emailmessage", "email_message", "EmailMessage"]
INFERENCE_SOURCE_TYPES = ["inference", "inferencerecord", "inference_record", "InferenceRecord"]


def _facts_for_email(email):
    return FactRecord.objects.filter(
        source_id=email.id,
        source_type__in=EMAIL_SOURCE_TYPES,
    ).order_by("-id")


def _inferences_for_email(email):
    return InferenceRecord.objects.filter(
        source_id=email.id,
        source_type__in=EMAIL_SOURCE_TYPES,
    ).order_by("-id")


def _proposals_for_email(email, inference_ids):
    return CRMUpdateProposal.objects.filter(
        target_entity_id__in=[email.id] + inference_ids
    ).order_by("-id")


def _recommendations_for_email(email, inference_ids):
    return AIRecommendation.objects.filter(
        scope_id__in=[email.id] + inference_ids
    ).order_by("-id")


def email_list_view(request):
    emails = EmailMessage.objects.all().order_by("-id")

    rows = []
    for email in emails:
        facts = _facts_for_email(email)
        inferences = _inferences_for_email(email)
        inference_ids = list(inferences.values_list("id", flat=True))
        proposals = _proposals_for_email(email, inference_ids)
        recommendations = _recommendations_for_email(email, inference_ids)

        rows.append({
            "email": email,
            "facts_count": facts.count(),
            "inferences_count": inferences.count(),
            "proposals_count": proposals.count(),
            "recommendations_count": recommendations.count(),
        })

    return render(
        request,
        "emailing/email_list.html",
        {
            "rows": rows,
        },
    )


def email_detail_view(request, pk):
    email = get_object_or_404(EmailMessage, pk=pk)

    facts = _facts_for_email(email)
    inferences = _inferences_for_email(email)
    inference_ids = list(inferences.values_list("id", flat=True))
    proposals = _proposals_for_email(email, inference_ids)
    recommendations = _recommendations_for_email(email, inference_ids)

    return render(
        request,
        "emailing/email_detail.html",
        {
            "email": email,
            "facts": facts,
            "inferences": inferences,
            "proposals": proposals,
            "recommendations": recommendations,
        },
    )
