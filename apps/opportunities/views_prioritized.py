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

    rows = build_prioritized_opportunities(
        stage=stage,
        needs_attention_only=needs_attention_only,
    )

    stats = {
        "visible_count": len(rows),
        "high_count": len([row for row in rows if row.priority_bucket == "high"]),
        "blocked_count": len([row for row in rows if row.execution_status == "blocked"]),
    }

    return render(
        request,
        "opportunities/prioritized.html",
        {
            "rows": rows,
            "stats": stats,
            "selected_stage": stage or "",
            "needs_attention_only": needs_attention_only,
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
    priority_row = build_opportunity_priority_row(opportunity)

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
