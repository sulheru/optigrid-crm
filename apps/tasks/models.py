# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/models.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import models


class CRMTask(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("dismissed", "Dismissed"),
    ]

    TASK_TYPE_CHOICES = [
        ("reply_email", "Reply Email"),
        ("follow_up", "Follow Up"),
        ("schedule_call", "Schedule Call"),
        ("prepare_proposal", "Prepare Proposal"),
        ("review_manually", "Review Manually"),
        ("opportunity_review", "Opportunity review"),
        ("qualification_review", "Qualification review"),
        ("pricing_review", "Pricing review"),
    ]

    SOURCE_CHOICES = [
        ("manual", "Manual"),
        ("auto", "Auto"),
    ]

    opportunity = models.ForeignKey(
        "opportunities.Opportunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    source_recommendation = models.ForeignKey(
        "recommendations.AIRecommendation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=20, default="normal")
    due_at = models.DateTimeField(null=True, blank=True)

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="manual",
    )
    source_action = models.CharField(max_length=100, blank=True)
    is_revoked = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.status}]"

    @property
    def is_auto(self):
        return self.source == "auto"

    @property
    def can_be_revoked(self):
        return self.is_auto and not self.is_revoked and self.status not in {"done", "dismissed"}

    @property
    def effective_status_label(self):
        if self.is_revoked:
            return "Revoked"
        return self.get_status_display()
