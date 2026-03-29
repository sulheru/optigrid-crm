from django.contrib import admin

from .models import MailboxAccount, OperatingOrganization


@admin.register(OperatingOrganization)
class OperatingOrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "primary_domain",
        "is_simulated",
        "status",
        "created_at",
    )
    list_filter = (
        "is_simulated",
        "status",
        "created_at",
    )
    search_fields = (
        "name",
        "slug",
        "legal_name",
        "primary_domain",
    )


@admin.register(MailboxAccount)
class MailboxAccountAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "display_name",
        "operating_organization",
        "provider",
        "account_key",
        "is_primary",
        "status",
    )
    list_filter = (
        "provider",
        "is_primary",
        "status",
        "operating_organization",
    )
    search_fields = (
        "email",
        "display_name",
        "account_key",
        "operating_organization__name",
    )
