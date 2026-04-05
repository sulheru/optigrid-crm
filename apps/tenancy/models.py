from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()


def normalize_domain(value: str) -> str:
    return (value or "").strip().lower()


def extract_domain(email: str) -> str:
    email = normalize_email(email)
    if "@" not in email:
        return ""
    return email.split("@", 1)[1]


class OperatingOrganization(models.Model):
    class Status(models.TextChoices):
        PROVISIONAL = "provisional", "Provisional"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    legal_name = models.CharField(max_length=255, blank=True)
    primary_domain = models.CharField(max_length=255, blank=True)
    is_simulated = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_operating_organizations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Operating Organization"
        verbose_name_plural = "Operating Organizations"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["primary_domain"]),
            models.Index(fields=["status"]),
        ]

    def clean(self):
        super().clean()
        self.primary_domain = normalize_domain(self.primary_domain)
        if not self.slug:
            self.slug = slugify(
                self.legal_name or self.name or self.primary_domain or "organization"
            )[:120]
        self.is_simulated = self.is_simulated or self.primary_domain.endswith(".sim")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CorporateDomain(models.Model):
    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.CASCADE,
        related_name="corporate_domains",
    )
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Corporate Domain"
        verbose_name_plural = "Corporate Domains"
        ordering = ["domain"]
        indexes = [
            models.Index(fields=["domain"], name="cd_dom_idx"),
            models.Index(fields=["operating_organization", "is_active"], name="cd_org_act_idx"),
        ]

    def clean(self):
        super().clean()
        self.domain = normalize_domain(self.domain)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.domain


class Identity(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"
        ARCHIVED = "archived", "Archived"

    email = models.EmailField(max_length=254, unique=True)
    display_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["email"]
        verbose_name = "Identity"
        verbose_name_plural = "Identities"

    def clean(self):
        super().clean()
        self.email = normalize_email(self.email)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class CorporateMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INVITED = "invited", "Invited"
        DISABLED = "disabled", "Disabled"
        ARCHIVED = "archived", "Archived"

    identity = models.ForeignKey(
        "tenancy.Identity",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    is_default = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Corporate Membership"
        verbose_name_plural = "Corporate Memberships"
        ordering = ["operating_organization__name", "identity__email"]
        constraints = [
            models.UniqueConstraint(
                fields=["identity", "operating_organization"],
                name="uniq_id_org",
            ),
            models.CheckConstraint(
                condition=Q(role__in=["owner", "admin", "member"]),
                name="corporate_membership_role_valid",
            ),
        ]
        indexes = [
            models.Index(fields=["operating_organization", "status"], name="cm_org_st_idx"),
            models.Index(fields=["identity", "status"], name="cm_id_st_idx"),
        ]

    def __str__(self):
        return f"{self.identity.email} @ {self.operating_organization.name}"


class MailboxAccount(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"
        ARCHIVED = "archived", "Archived"

    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.CASCADE,
        related_name="mailbox_accounts",
    )
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="mailbox_accounts",
    )
    display_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=254)
    account_key = models.CharField(max_length=120)
    provider = models.CharField(max_length=100, default="mail_stub")
    is_primary = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mailbox Account"
        verbose_name_plural = "Mailbox Accounts"
        ordering = ["operating_organization__name", "email"]
        constraints = [
            models.UniqueConstraint(
                fields=["operating_organization", "email"],
                name="uniq_mailbox_org_email",
            ),
            models.UniqueConstraint(
                fields=["operating_organization", "account_key"],
                name="uniq_mailbox_org_key",
            ),
        ]

    @property
    def corporation(self):
        return self.operating_organization

    def clean(self):
        super().clean()
        self.email = normalize_email(self.email)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class PublicEmailDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["domain"]
        indexes = [
            models.Index(fields=["domain"]),
            models.Index(fields=["is_active"]),
        ]

    def clean(self):
        super().clean()
        self.domain = normalize_domain(self.domain)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.domain


class EmailIdentity(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"
        ARCHIVED = "archived", "Archived"

    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.CASCADE,
        related_name="email_identities",
    )
    email = models.EmailField(max_length=254, unique=True)
    display_name = models.CharField(max_length=200, blank=True)
    account_key = models.CharField(max_length=120, unique=True)
    provider = models.CharField(max_length=100, default="system")
    is_primary = models.BooleanField(default=False)
    is_public_domain = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["email"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["operating_organization", "status"]),
        ]

    @property
    def corporation(self):
        return self.operating_organization

    def clean(self):
        super().clean()
        self.email = normalize_email(self.email)
        if not self.account_key:
            self.account_key = self.email

        email_domain = extract_domain(self.email)
        self.is_public_domain = PublicEmailDomain.objects.filter(
            domain=email_domain,
            is_active=True,
        ).exists()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email
