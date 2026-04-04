from django.contrib import admin

from apps.emailing.models import (
    InboundDecision,
    InboundEmail,
    InboundInterpretation,
    OutboundEmail,
)


@admin.register(OutboundEmail)
class OutboundEmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "to_email",
        "status",
        "email_type",
        "operating_organization",
        "mailbox_account",
        "created_at",
    )
    list_filter = ("status", "email_type", "operating_organization")
    search_fields = ("subject", "to_email", "body")


@admin.register(InboundEmail)
class InboundEmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "from_email",
        "reply_type",
        "status",
        "operating_organization",
        "mailbox_account",
        "received_at",
    )
    list_filter = ("status", "reply_type", "operating_organization")
    search_fields = ("subject", "from_email", "body")


@admin.register(InboundInterpretation)
class InboundInterpretationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "inbound_email",
        "intent",
        "recommended_action",
        "urgency",
        "sentiment",
        "confidence",
        "created_at",
    )
    list_filter = ("intent", "recommended_action", "urgency", "sentiment")
    search_fields = ("rationale",)


@admin.register(InboundDecision)
class InboundDecisionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "inbound_email",
        "action_type",
        "status",
        "priority",
        "requires_approval",
        "applied_automatically",
        "created_at",
    )
    list_filter = ("action_type", "status", "priority", "requires_approval")
    search_fields = ("summary", "automation_reason")
