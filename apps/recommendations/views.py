from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.recommendations.models import AIRecommendation


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
            "recommendation_type",
            flat=True,
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

    messages.warning(
        request,
        (
            f"Recommendation #{recommendation.id} found, but task materialization "
            "is not implemented yet in this module."
        ),
    )
    return redirect("/recommendations/")


@require_POST
def recommendation_dismiss(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)

    if recommendation.status == "dismissed":
        messages.info(request, "Already dismissed.")
        return redirect("/recommendations/")

    recommendation.status = "dismissed"
    recommendation.save(update_fields=["status"])

    messages.success(request, "Recommendation dismissed.")
    return redirect("/recommendations/")
