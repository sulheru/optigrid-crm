# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/models.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import models


class Opportunity(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("qualified", "Qualified"),
        ("proposal", "Proposal"),
        ("won", "Won"),
        ("lost", "Lost"),
    ]

    source_task = models.ForeignKey(
        "tasks.CRMTask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )

    source_recommendation = models.ForeignKey(
        "recommendations.AIRecommendation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spawned_opportunities",
    )

    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    stage = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    confidence = models.FloatField(default=0.0)
    summary = models.TextField(blank=True)

    last_analyzed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.stage}]"
