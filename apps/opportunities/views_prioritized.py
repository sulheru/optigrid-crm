# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/views_prioritized.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.shortcuts import get_object_or_404, render

from apps.opportunities.models import Opportunity
from apps.opportunities.services.prioritization import (
    build_opportunity_priority_row,
    build_prioritized_opportunities,
)
from apps.tasks.models import CRMTask


def prioritized_opportunities_view(request):
    stage = (request.GET.get("stage") or "").strip() or None
    needs_attention_only = request.GET.get("needs_attention") in {"1", "true", "yes"}

    filter_high = request.GET.get("high") == "1"
    filter_autotasks = request.GET.get("autotasks") == "1"
    filter_no_action = request.GET.get("no_action") == "1"
    filter_risk = request.GET.get("risk") == "1"

    rows = build_prioritized_opportunities(
        stage=stage,
        needs_attention_only=needs_attention_only,
    )
    rows = [row.to_dict() for row in rows]

    if filter_high:
        rows = [r for r in rows if r["priority_bucket"] == "high"]

    if filter_autotasks:
        rows = [r for r in rows if r["has_autotasks"]]

    if filter_no_action:
        rows = [r for r in rows if not r["has_open_tasks"]]

    if filter_risk:
        rows = [r for r in rows if r["has_risk"]]

    stats = {
        "visible_count": len(rows),
        "high_count": len([r for r in rows if r["priority_bucket"] == "high"]),
        "blocked_count": len([r for r in rows if r["execution_status"] == "blocked"]),
    }

    return render(
        request,
        "opportunities/prioritized.html",
        {
            "rows": rows,
            "stats": stats,
            "selected_stage": stage or "",
            "needs_attention_only": needs_attention_only,
            "filters": {
                "high": filter_high,
                "autotasks": filter_autotasks,
                "no_action": filter_no_action,
                "risk": filter_risk,
            },
            "stage_choices": [
                ("", "All"),
                ("new", "New"),
                ("qualified", "Qualified"),
                ("proposal", "Proposal"),
            ],
        },
    )


def opportunity_tasks_view(request, pk: int):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    priority_row = build_opportunity_priority_row(opportunity).to_dict()

    tasks = CRMTask.objects.filter(opportunity=opportunity).order_by("-created_at", "-id")
    open_tasks = [task for task in tasks if task.status in {"open", "in_progress"}]
    auto_tasks = [task for task in tasks if task.source == "auto"]

    return render(
        request,
        "opportunities/opportunity_tasks.html",
        {
            "opportunity": opportunity,
            "priority_row": priority_row,
            "tasks": tasks,
            "open_tasks_count": len(open_tasks),
            "auto_tasks_count": len(auto_tasks),
        },
    )

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.opportunities.models import Opportunity


@require_POST
def opportunity_set_stage_view(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)

    target_stage = (request.POST.get("stage") or "").strip()
    next_url = (request.POST.get("next") or "").strip() or "/opportunities/prioritized/"

    valid_stages = {choice[0] for choice in Opportunity.STAGE_CHOICES}
    if target_stage not in valid_stages:
        messages.error(request, f"Invalid stage: {target_stage}")
        return redirect(next_url)

    current_stage = opportunity.stage
    if current_stage == target_stage:
        messages.info(request, f"Opportunity already in stage '{target_stage}'.")
        return redirect(next_url)

    opportunity.stage = target_stage
    opportunity.save(update_fields=["stage", "updated_at"])

    messages.success(
        request,
        f"Opportunity #{opportunity.id} stage changed: {current_stage} → {target_stage}.",
    )
    return redirect(next_url)
