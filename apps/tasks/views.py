# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/views.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CRMTask


def tasks_list_view(request):
    source = request.GET.get("source", "all")
    status = request.GET.get("status", "all")
    revoked = request.GET.get("revoked", "active")
    source_action = request.GET.get("source_action", "all")

    tasks = CRMTask.objects.select_related("opportunity").all().order_by(
        "is_revoked",
        "-created_at",
    )

    if source != "all":
        tasks = tasks.filter(source=source)

    if status != "all":
        tasks = tasks.filter(status=status)

    if revoked == "revoked":
        tasks = tasks.filter(is_revoked=True)
    elif revoked == "all":
        pass
    else:
        tasks = tasks.filter(is_revoked=False)

    if source_action != "all":
        if source_action == "empty":
            tasks = tasks.filter(source_action="")
        else:
            tasks = tasks.filter(source_action=source_action)

    base_qs = CRMTask.objects.all()

    source_action_values = (
        CRMTask.objects.exclude(source_action="")
        .values_list("source_action", flat=True)
        .distinct()
        .order_by("source_action")
    )

    context = {
        "tasks": tasks,
        "filters": {
            "source": source,
            "status": status,
            "revoked": revoked,
            "source_action": source_action,
        },
        "source_action_values": source_action_values,
        "counts": {
            "all": base_qs.count(),
            "auto": base_qs.filter(source="auto").count(),
            "manual": base_qs.filter(source="manual").count(),
            "open": base_qs.filter(status="open", is_revoked=False).count(),
            "in_progress": base_qs.filter(status="in_progress", is_revoked=False).count(),
            "done": base_qs.filter(status="done", is_revoked=False).count(),
            "dismissed": base_qs.filter(status="dismissed", is_revoked=False).count(),
            "revoked": base_qs.filter(is_revoked=True).count(),
        },
    }
    return render(request, "tasks/list.html", context)


@require_POST
def revoke_task(request, task_id):
    task = get_object_or_404(CRMTask, pk=task_id)

    if task.source != "auto":
        messages.warning(request, "Solo se pueden revocar tasks automáticas.")
        return redirect(request.META.get("HTTP_REFERER", "/tasks/"))

    if task.is_revoked:
        messages.info(request, "La task ya estaba revocada.")
        return redirect(request.META.get("HTTP_REFERER", "/tasks/"))

    task.is_revoked = True
    task.save(update_fields=["is_revoked", "updated_at"])

    messages.success(request, "Task revocada. El sistema no la recreará automáticamente.")
    return redirect(request.META.get("HTTP_REFERER", "/tasks/"))
