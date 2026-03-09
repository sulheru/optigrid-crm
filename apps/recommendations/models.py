from django.db import models


class AIRecommendation(models.Model):
    STATUS_NEW = "new"
    STATUS_MATERIALIZED = "materialized"
    STATUS_DISMISSED = "dismissed"
    STATUS_EXECUTED = "executed"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_MATERIALIZED, "Materialized"),
        (STATUS_DISMISSED, "Dismissed"),
        (STATUS_EXECUTED, "Executed"),
    ]

    scope_type = models.CharField(max_length=50)
    scope_id = models.CharField(max_length=100)
    recommendation_type = models.CharField(max_length=100)
    recommendation_text = models.TextField()
    confidence = models.FloatField()
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)
