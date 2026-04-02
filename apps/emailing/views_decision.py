from django.shortcuts import get_object_or_404, render

from .decision_detail import build_email_decision_context
from .models import InboundEmail


def email_decision_detail(request, pk):
    """
    Primera vista útil de transparencia de decisión para un email real.
    """
    email_obj = get_object_or_404(InboundEmail, pk=pk)
    context = build_email_decision_context(email_obj)
    return render(request, "emailing/decision_detail.html", context)
