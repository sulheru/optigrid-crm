# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/lead_research/models.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import models
from django.utils import timezone


class LeadSuggestion(models.Model):
    STATUS_NEW = "new"
    STATUS_APPROVED = "approved"
    STATUS_DISMISSED = "dismissed"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DISMISSED, "Dismissed"),
    ]

    company = models.ForeignKey(
        "companies.Company",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lead_suggestions",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    company_name = models.CharField(max_length=255)
    normalized_company_name = models.CharField(max_length=255, db_index=True)
    website = models.URLField(blank=True, default="")
    website_domain = models.CharField(max_length=255, blank=True, default="", db_index=True)
    country = models.CharField(max_length=100, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    industry = models.CharField(max_length=100, blank=True, default="")
    employee_range = models.CharField(max_length=100, blank=True, default="")

    fit_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    timing_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    novelty_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    source_query = models.CharField(max_length=500, blank=True, default="")
    source_provider = models.CharField(max_length=100, blank=True, default="gemini_mock")
    rationale_codes = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    first_seen_at = models.DateTimeField(default=timezone.now)
    last_seen_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fit_score", "-timing_score", "-novelty_score", "-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["status", "normalized_company_name"]),
            models.Index(fields=["status", "website_domain"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["normalized_company_name", "website_domain"],
                name="lead_suggestion_unique_name_domain",
            )
        ]

    def __str__(self):
        return f"{self.company_name} [{self.status}]"


class LeadSignal(models.Model):
    SIGNAL_FUNDING = "funding"
    SIGNAL_HIRING = "hiring"
    SIGNAL_EXPANSION = "expansion"
    SIGNAL_GROWTH = "growth"
    SIGNAL_TECH = "tech"
    SIGNAL_TRIGGER = "trigger"

    SIGNAL_TYPE_CHOICES = [
        (SIGNAL_FUNDING, "Funding"),
        (SIGNAL_HIRING, "Hiring"),
        (SIGNAL_EXPANSION, "Expansion"),
        (SIGNAL_GROWTH, "Growth"),
        (SIGNAL_TECH, "Tech"),
        (SIGNAL_TRIGGER, "Trigger"),
    ]

    suggestion = models.ForeignKey(
        LeadSuggestion,
        on_delete=models.CASCADE,
        related_name="signals",
    )

    signal_type = models.CharField(max_length=50, choices=SIGNAL_TYPE_CHOICES)
    signal_value = models.CharField(max_length=255, blank=True, default="")
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    source_provider = models.CharField(max_length=100, blank=True, default="gemini_mock")
    source_ref = models.CharField(max_length=500, blank=True, default="")
    observed_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-confidence", "-created_at"]
        indexes = [
            models.Index(fields=["signal_type", "created_at"]),
            models.Index(fields=["suggestion", "signal_type"]),
        ]

    def __str__(self):
        return f"{self.suggestion.company_name} · {self.signal_type}"


class LeadResearchSnapshot(models.Model):
    suggestion = models.OneToOneField(
        LeadSuggestion,
        on_delete=models.CASCADE,
        related_name="snapshot",
    )

    discovery_payload = models.JSONField(default=dict, blank=True)
    enrichment_payload = models.JSONField(default=dict, blank=True)
    hypothesis_payload = models.JSONField(default=dict, blank=True)

    summary_codes = models.JSONField(default=list, blank=True)
    model_name = models.CharField(max_length=100, blank=True, default="")
    prompt_version = models.CharField(max_length=50, blank=True, default="v1")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Snapshot<{self.suggestion.company_name}>"
