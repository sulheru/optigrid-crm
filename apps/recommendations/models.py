from django.db import models
from apps.tenancy.models import MailboxAccount, OperatingOrganization


class AIRecommendation(models.Model):
    operating_organization = models.ForeignKey(
        OperatingOrganization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommendations",
    )
    mailbox_account = models.ForeignKey(
        MailboxAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommendations",
    )

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

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.recommendation_type} [{self.status}] #{self.id}"


class ExecutionLog(models.Model):
    STATUS_STARTED = "started"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_BLOCKED = "blocked"

    STATUS_CHOICES = [
        (STATUS_STARTED, "Started"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_BLOCKED, "Blocked"),
    ]

    recommendation = models.ForeignKey(
        "recommendations.AIRecommendation",
        on_delete=models.CASCADE,
        related_name="execution_logs",
    )
    action_type = models.CharField(max_length=64)
    request_payload = models.JSONField(default=dict, blank=True)
    result_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_STARTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["recommendation", "action_type"],
                name="uniq_executionlog_recommendation_action",
            )
        ]
        indexes = [
            models.Index(fields=["recommendation", "status"], name="reco_execlog_status_idx"),
        ]

    def __str__(self):
        return f"ExecutionLog(recommendation={self.recommendation_id}, action={self.action_type}, status={self.status})"
