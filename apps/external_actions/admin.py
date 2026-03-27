from django.contrib import admin

from .models import ExternalActionIntent


@admin.register(ExternalActionIntent)
class ExternalActionIntentAdmin(admin.ModelAdmin):
    list_display = (
        "public_id",
        "intent_type",
        "port_name",
        "provider",
        "policy_classification",
        "approval_status",
        "execution_status",
        "dispatch_status",
        "created_at",
    )
    list_filter = (
        "intent_type",
        "port_name",
        "provider",
        "policy_classification",
        "approval_status",
        "execution_status",
        "dispatch_status",
    )
    search_fields = (
        "public_id",
        "idempotency_key",
        "target_ref_type",
        "target_ref_id",
        "source_id",
        "last_error_code",
        "last_error_message",
    )
    readonly_fields = (
        "public_id",
        "created_at",
        "updated_at",
        "approved_at",
        "last_attempt_at",
        "dispatched_at",
        "completed_at",
    )
