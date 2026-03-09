from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.recommendations.models import AIRecommendation
from apps.recommendations.services import (
    dismiss_recommendation,
    materialize_recommendation,
)


def recommendation_list(request):

    qs = AIRecommendation.objects.all().order_by("-id")

    status = request.GET.get("status")
    rtype = request.GET.get("recommendation_type")

    if status:
        qs = qs.filter(status=status)

    if rtype:
        qs = qs.filter(recommendation_type=rtype)

    recommendation_types = (
        AIRecommendation.objects.values_list(
            "recommendation_type", flat=True
        ).distinct()
    )

    context = {
        "recommendations": qs[:200],
        "status": status,
        "rtype": rtype,
        "recommendation_types": recommendation_types,
        "status_choices": AIRecommendation.STATUS_CHOICES,
    }

    return render(request, "recommendations/recommendation_list.html", context)


@require_POST
def recommendation_create_task(request, pk):

    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    task, created = materialize_recommendation(recommendation)

    if created:
        messages.success(request, f"Task #{task.id} created.")
    else:
        messages.info(request, f"Task #{task.id} reused.")

    return redirect("/recommendations/")


@require_POST
def recommendation_dismiss(request, pk):

    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    _, changed = dismiss_recommendation(recommendation)

    if changed:
        messages.success(request, "Recommendation dismissed.")
    else:
        messages.info(request, "Already dismissed.")

    return redirect("/recommendations/")
