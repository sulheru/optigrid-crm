from django.contrib import admin

from .models import (
    CorporateDomain,
    CorporateMembership,
    Identity,
    MailboxAccount,
    OperatingOrganization,
)


class CorporateDomainInline(admin.TabularInline):
    model = CorporateDomain
    extra = 0
    fields = ("domain", "is_primary", "is_active", "notes")
    show_change_link = True


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
    inlines = [CorporateDomainInline]


@admin.register(CorporateDomain)
class CorporateDomainAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "operating_organization",
        "is_primary",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_primary",
        "is_active",
        "operating_organization",
    )
    search_fields = (
        "domain",
        "operating_organization__name",
        "operating_organization__slug",
    )


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "display_name",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "email",
        "display_name",
    )


@admin.register(CorporateMembership)
class CorporateMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "identity",
        "operating_organization",
        "role",
        "status",
        "is_default",
        "created_at",
    )
    list_filter = (
        "role",
        "status",
        "is_default",
        "operating_organization",
    )
    search_fields = (
        "identity__email",
        "identity__display_name",
        "operating_organization__name",
        "operating_organization__slug",
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
