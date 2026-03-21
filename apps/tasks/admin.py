# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/admin.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.contrib import admin

from .models import CRMTask


@admin.register(CRMTask)
class CRMTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "task_type",
        "status",
        "priority",
        "source",
        "source_action",
        "is_revoked",
        "opportunity",
        "source_recommendation",
        "created_at",
    )
    list_filter = (
        "task_type",
        "status",
        "priority",
        "source",
        "is_revoked",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "source_action",
        "opportunity__title",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("opportunity", "source_recommendation")
