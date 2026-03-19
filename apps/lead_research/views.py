from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.lead_research.models import LeadSuggestion
from apps.lead_research.services.lead_promotion import promote_lead_to_opportunity


def lead_list_view(request):
    status = request.GET.get("status", "new")

    qs = LeadSuggestion.objects.all()
    if status != "all":
        qs = qs.filter(status=status)
    qs = qs.order_by("-fit_score", "-timing_score", "-created_at")

    context = {
        "leads": qs[:100],
        "status": status,
        "counts": {
            "new": LeadSuggestion.objects.filter(status="new").count(),
            "approved": LeadSuggestion.objects.filter(status="approved").count(),
            "dismissed": LeadSuggestion.objects.filter(status="dismissed").count(),
        },
    }
    return render(request, "lead_research/list.html", context)


def approve_lead(request, pk):
    obj = get_object_or_404(LeadSuggestion, pk=pk)

    obj.status = LeadSuggestion.STATUS_APPROVED
    if not obj.approved_at:
        obj.approved_at = timezone.now()
    obj.save()

    promote_lead_to_opportunity(obj)

    return redirect(request.META.get("HTTP_REFERER", "/leads/"))


def dismiss_lead(request, pk):
    obj = get_object_or_404(LeadSuggestion, pk=pk)
    obj.status = LeadSuggestion.STATUS_DISMISSED
    obj.dismissed_at = timezone.now()
    obj.save()
    return redirect(request.META.get("HTTP_REFERER", "/leads/"))


def reopen_lead(request, pk):
    obj = get_object_or_404(LeadSuggestion, pk=pk)
    obj.status = LeadSuggestion.STATUS_NEW
    obj.dismissed_at = None
    obj.approved_at = None
    obj.save()
    return redirect(request.META.get("HTTP_REFERER", "/leads/"))
