from django.http import Http404
from django.shortcuts import render

from apps.emailing.decision_detail import get_email_decision_view
from apps.emailing.models import InboundEmail


def email_decision_detail(request, email_id: int):
    try:
        context = get_email_decision_view(email_id)
    except InboundEmail.DoesNotExist as exc:
        raise Http404("Email not found") from exc

    return render(request, "emailing/decision_detail.html", context)
