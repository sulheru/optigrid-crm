from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CRMTask


def tasks_list_view(request):
    tasks = CRMTask.objects.select_related("opportunity").all()
    return render(request, "tasks/list.html", {"tasks": tasks})


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
