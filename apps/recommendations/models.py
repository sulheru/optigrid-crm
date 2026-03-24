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

    SOURCE_RULES = "rules"
    SOURCE_LLM = "llm"
    SOURCE_MERGED = "merged"

    SOURCE_CHOICES = [
        (SOURCE_RULES, "Rules"),
        (SOURCE_LLM, "LLM"),
        (SOURCE_MERGED, "Merged"),
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

    source = models.CharField(
        max_length=16,
        choices=SOURCE_CHOICES,
        default=SOURCE_RULES,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
