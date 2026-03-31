from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class OperatingOrganization(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    legal_name = models.CharField(max_length=255, blank=True)
    primary_domain = models.CharField(max_length=255, blank=True)
    is_simulated = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_operating_organizations",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Operating Organization"
        verbose_name_plural = "Operating Organizations"

    def save(self, *args, **kwargs):
        if self.primary_domain:
            self.primary_domain = self.primary_domain.strip().lower()

        if not self.slug:
            base = slugify(self.name)[:100] or "org"
            slug = base
            i = 2
            while OperatingOrganization.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                suffix = f"-{i}"
                slug = f"{base[: max(1, 120 - len(suffix))]}{suffix}"
                i += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def corporation(self):
        return self

    def __str__(self):
        sim = " [SIM]" if self.is_simulated else ""
        return f"{self.name}{sim}"


class CorporateDomain(models.Model):
    operating_organization = models.ForeignKey(
        OperatingOrganization,
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
        ordering = ["domain"]
        verbose_name = "Corporate Domain"
        verbose_name_plural = "Corporate Domains"
        indexes = [
            models.Index(fields=["domain"], name="cd_dom_idx"),
            models.Index(fields=["operating_organization", "is_active"], name="cd_org_act_idx"),
        ]

    def save(self, *args, **kwargs):
        self.domain = self.domain.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.domain} → {self.operating_organization.name}"


class Identity(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"
        ARCHIVED = "archived", "Archived"

    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["email"]
        verbose_name = "Identity"
        verbose_name_plural = "Identities"

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def email_domain(self) -> str:
        if "@" not in self.email:
            return ""
        return self.email.split("@", 1)[1].strip().lower()

    def __str__(self):
        return self.display_name or self.email


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
        Identity,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    operating_organization = models.ForeignKey(
        OperatingOrganization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_default = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["operating_organization__name", "identity__email"]
        verbose_name = "Corporate Membership"
        verbose_name_plural = "Corporate Memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["identity", "operating_organization"],
                name="uniq_id_org",
            )
        ]
        indexes = [
            models.Index(fields=["operating_organization", "status"], name="cm_org_st_idx"),
            models.Index(fields=["identity", "status"], name="cm_id_st_idx"),
        ]

    def __str__(self):
        return f"{self.identity.email} @ {self.operating_organization.name} [{self.role}]"


class MailboxAccount(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"
        ARCHIVED = "archived", "Archived"

    operating_organization = models.ForeignKey(
        OperatingOrganization,
        on_delete=models.CASCADE,
        related_name="mailbox_accounts",
    )

    display_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    account_key = models.CharField(max_length=120)
    provider = models.CharField(max_length=100, default="mail_stub")
    is_primary = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mailbox_accounts",
    )

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["operating_organization__name", "email"]
        unique_together = (
            ("operating_organization", "email"),
            ("operating_organization", "account_key"),
        )
        verbose_name = "Mailbox Account"
        verbose_name_plural = "Mailbox Accounts"

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def corporation(self):
        return self.operating_organization

    @property
    def email_domain(self) -> str:
        if "@" not in self.email:
            return ""
        return self.email.split("@", 1)[1].strip().lower()

    def __str__(self):
        label = self.display_name or self.email
        return f"{self.operating_organization.name} — {label}"
