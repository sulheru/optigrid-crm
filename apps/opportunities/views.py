# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/views.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.contrib import messages
from django.db.models import F
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Opportunity


ALLOWED_SORTS = {
    "updated_at": "-updated_at",
    "-updated_at": "updated_at",
    "created_at": "-created_at",
    "-created_at": "created_at",
    "estimated_value": "estimated_value",
    "-estimated_value": "-estimated_value",
    "confidence": "confidence",
    "-confidence": "-confidence",
    "title": "title",
    "-title": "-title",
}

STAGE_CHOICES = ["new", "qualified", "proposal", "won", "lost"]

STAGE_TRANSITIONS = {
    "new": ["qualified"],
    "qualified": ["proposal", "lost"],
    "proposal": ["won", "lost"],
    "won": [],
    "lost": [],
}


def _normalize_sort(sort_value: str) -> str:
    if sort_value in ALLOWED_SORTS:
        return ALLOWED_SORTS[sort_value]
    return "-updated_at"


def list_opportunities(request):
    qs = Opportunity.objects.all()

    stage = (request.GET.get("stage") or "").strip()
    sort = (request.GET.get("sort") or "-updated_at").strip()

    if stage and stage in STAGE_CHOICES:
        qs = qs.filter(stage=stage)

    sort_field = _normalize_sort(sort)

    # Nulls-last razonable para estimated_value y confidence en PostgreSQL/Django 6
    if sort_field in ("estimated_value", "-estimated_value"):
        descending = sort_field.startswith("-")
        field_name = "estimated_value"
        qs = qs.order_by(
            F(field_name).desc(nulls_last=True) if descending else F(field_name).asc(nulls_last=True),
            F("updated_at").desc(nulls_last=True),
        )
    elif sort_field in ("confidence", "-confidence"):
        descending = sort_field.startswith("-")
        field_name = "confidence"
        qs = qs.order_by(
            F(field_name).desc(nulls_last=True) if descending else F(field_name).asc(nulls_last=True),
            F("updated_at").desc(nulls_last=True),
        )
    else:
        qs = qs.order_by(sort_field)

    context = {
        "opportunities": qs,
        "current_stage": stage,
        "current_sort": sort_field,
        "stage_choices": STAGE_CHOICES,
        "stage_transitions": STAGE_TRANSITIONS,
        "total_results": qs.count(),
    }
    return render(request, "opportunities/list.html", context)


def transition_opportunity_stage(request, pk: int):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    opportunity = get_object_or_404(Opportunity, pk=pk)
    target_stage = (request.POST.get("stage") or "").strip()

    if target_stage not in STAGE_CHOICES:
        messages.error(request, "Stage inválido.")
        return redirect(request.META.get("HTTP_REFERER") or reverse("opportunities:list"))

    allowed_targets = STAGE_TRANSITIONS.get(opportunity.stage, [])
    if target_stage not in allowed_targets:
        messages.error(
            request,
            f"No se permite transición de '{opportunity.stage}' a '{target_stage}'.",
        )
        return redirect(request.META.get("HTTP_REFERER") or reverse("opportunities:list"))

    previous_stage = opportunity.stage
    opportunity.stage = target_stage
    opportunity.save(update_fields=["stage", "updated_at"])

    messages.success(
        request,
        f"Opportunity #{opportunity.pk} movida de '{previous_stage}' a '{target_stage}'.",
    )
    return redirect(request.META.get("HTTP_REFERER") or reverse("opportunities:list"))
