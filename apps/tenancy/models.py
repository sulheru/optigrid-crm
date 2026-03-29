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

    def __str__(self):
        sim = " [SIM]" if self.is_simulated else ""
        return f"{self.name}{sim}"


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

    def __str__(self):
        label = self.display_name or self.email
        return f"{self.operating_organization.name} — {label}"
