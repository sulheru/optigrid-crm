from django.contrib import admin

from apps.recommendations.models import AIRecommendation, ExecutionLog


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recommendation_type",
        "scope_type",
        "scope_id",
        "status",
        "source",
        "operating_organization",
        "mailbox_account",
        "created_at",
    )
    list_filter = ("recommendation_type", "status", "source", "operating_organization")
    search_fields = ("recommendation_text", "scope_type", "scope_id")


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recommendation",
        "action_type",
        "status",
        "created_at",
    )
    list_filter = ("action_type", "status")
    search_fields = ("recommendation__id", "action_type")
    readonly_fields = ("created_at",)
