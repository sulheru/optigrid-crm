from django.contrib import admin

from .models import (
    CorporateDomain,
    CorporateMembership,
    EmailIdentity,
    Identity,
    MailboxAccount,
    OperatingOrganization,
    PublicEmailDomain,
)


@admin.register(OperatingOrganization)
class OperatingOrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "primary_domain", "status", "is_simulated")
    search_fields = ("name", "slug", "primary_domain")
    list_filter = ("status", "is_simulated")


@admin.register(MailboxAccount)
class MailboxAccountAdmin(admin.ModelAdmin):
    list_display = ("email", "operating_organization", "provider", "status", "is_primary")
    search_fields = ("email", "account_key", "display_name")
    list_filter = ("status", "provider", "is_primary")


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ("email", "display_name", "status")
    search_fields = ("email", "display_name")
    list_filter = ("status",)


@admin.register(CorporateMembership)
class CorporateMembershipAdmin(admin.ModelAdmin):
    list_display = ("identity", "operating_organization", "role", "status", "is_default")
    search_fields = ("identity__email", "operating_organization__name")
    list_filter = ("role", "status", "is_default")


@admin.register(CorporateDomain)
class CorporateDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "operating_organization", "is_primary", "is_active")
    search_fields = ("domain", "operating_organization__name")
    list_filter = ("is_primary", "is_active")


@admin.register(PublicEmailDomain)
class PublicEmailDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "is_active")
    search_fields = ("domain",)
    list_filter = ("is_active",)


@admin.register(EmailIdentity)
class EmailIdentityAdmin(admin.ModelAdmin):
    list_display = ("email", "operating_organization", "provider", "status", "is_primary", "is_public_domain")
    search_fields = ("email", "account_key", "display_name")
    list_filter = ("status", "provider", "is_primary", "is_public_domain")
