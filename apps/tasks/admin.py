from django.contrib import admin

from .models import CRMTask


@admin.register(CRMTask)
class CRMTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "task_type", "status", "priority", "created_at")
    list_filter = ("task_type", "status", "priority")
    search_fields = ("title", "description")
