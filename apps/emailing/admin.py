from django.contrib import admin

from apps.emailing.models import InboundEmail, OutboundEmail


@admin.register(InboundEmail)
class InboundEmailAdmin(admin.ModelAdmin):
    list_display = ("id", "from_email", "subject", "received_at")
    search_fields = ("from_email", "subject")


@admin.register(OutboundEmail)
class OutboundEmailAdmin(admin.ModelAdmin):
    list_display = ("id", "to_email", "subject", "status", "created_at")
    search_fields = ("to_email", "subject")
