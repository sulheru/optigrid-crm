import uuid

from django.conf import settings
from django.db import models
from apps.tenancy.models import MailboxAccount, OperatingOrganization
from django.utils import timezone


class ExternalActionIntent(models.Model):
    operating_organization = models.ForeignKey(
        OperatingOrganization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="external_action_intents",
    )
    mailbox_account = models.ForeignKey(
        MailboxAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="external_action_intents",
    )
    class IntentType(models.TextChoices):
        EMAIL_CREATE_DRAFT = "email.create_draft", "Email: Create Draft"
        EMAIL_SEND = "email.send", "Email: Send"
        CALENDAR_CREATE_EVENT = "calendar.create_event", "Calendar: Create Event"
        CALENDAR_UPDATE_EVENT = "calendar.update_event", "Calendar: Update Event"

    class PolicyClassification(models.TextChoices):
        AUTOMATIC = "automatic", "Automatic"
        REVIEWABLE = "reviewable", "Reviewable"
        CRITICAL = "critical", "Critical"

    class ApprovalStatus(models.TextChoices):
        NOT_REQUIRED = "not_required", "Not Required"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    class DispatchStatus(models.TextChoices):
        NOT_DISPATCHED = "not_dispatched", "Not Dispatched"
        READY = "ready", "Ready"
        DISPATCHED = "dispatched", "Dispatched"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class ExecutionStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        VALIDATED = "validated", "Validated"
        BLOCKED = "blocked", "Blocked"
        DRY_RUN_READY = "dry_run_ready", "Dry Run Ready"
        READY_TO_EXECUTE = "ready_to_execute", "Ready To Execute"
        EXECUTING = "executing", "Executing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        SUPERSEDED = "superseded", "Superseded"

    class SourceKind(models.TextChoices):
        RECOMMENDATION = "recommendation", "Recommendation"
        TASK = "task", "Task"
        CHAT = "chat", "Chat"
        WORKFLOW = "workflow", "Workflow"
        SYSTEM_RULE = "system_rule", "System Rule"
        USER_ACTION = "user_action", "User Action"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    intent_type = models.CharField(max_length=64, choices=IntentType.choices)
    port_name = models.CharField(max_length=32)
    adapter_key = models.CharField(max_length=64, blank=True, default="")
    provider = models.CharField(max_length=32, blank=True, default="")

    target_ref_type = models.CharField(max_length=64, blank=True, default="")
    target_ref_id = models.CharField(max_length=64, blank=True, default="")

    source_kind = models.CharField(
        max_length=32,
        choices=SourceKind.choices,
        default=SourceKind.RECOMMENDATION,
    )
    source_id = models.CharField(max_length=64, blank=True, default="")

    recommendation = models.ForeignKey(
        "recommendations.AIRecommendation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="external_action_intents",
    )
    task = models.ForeignKey(
        "tasks.CRMTask",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="external_action_intents",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_external_action_intents",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_external_action_intents",
    )

    payload = models.JSONField(default=dict, blank=True)
    normalized_preview = models.JSONField(default=dict, blank=True)

    policy_classification = models.CharField(
        max_length=16,
        choices=PolicyClassification.choices,
        default=PolicyClassification.REVIEWABLE,
    )
    approval_required = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=24,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.NOT_REQUIRED,
    )
    dispatch_status = models.CharField(
        max_length=24,
        choices=DispatchStatus.choices,
        default=DispatchStatus.NOT_DISPATCHED,
    )
    execution_status = models.CharField(
        max_length=24,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.DRAFT,
    )

    idempotency_key = models.CharField(max_length=255, blank=True, default="", db_index=True)
    idempotency_scope = models.CharField(max_length=32, blank=True, default="provider_account")

    risk_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    reason = models.TextField(blank=True, default="")
    rationale = models.TextField(blank=True, default="")
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    dry_run_supported = models.BooleanField(default=True)

    last_error_code = models.CharField(max_length=64, blank=True, default="")
    last_error_message = models.TextField(blank=True, default="")
    attempt_count = models.PositiveIntegerField(default=0)

    approved_at = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["intent_type"]),
            models.Index(fields=["port_name"]),
            models.Index(fields=["provider"]),
            models.Index(fields=["approval_status"]),
            models.Index(fields=["execution_status"]),
            models.Index(fields=["dispatch_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.intent_type} [{self.execution_status}]"

    def requires_human_approval(self) -> bool:
        return self.approval_required or self.approval_status == self.ApprovalStatus.PENDING_APPROVAL

    def mark_pending_approval(self) -> None:
        self.approval_required = True
        self.approval_status = self.ApprovalStatus.PENDING_APPROVAL

    def mark_approved(self, user=None) -> None:
        self.approval_required = True
        self.approval_status = self.ApprovalStatus.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()

    def mark_blocked(self, reason: str) -> None:
        self.execution_status = self.ExecutionStatus.BLOCKED
        self.last_error_code = "blocked"
        self.last_error_message = reason

    def mark_ready(self) -> None:
        self.dispatch_status = self.DispatchStatus.READY
        self.execution_status = self.ExecutionStatus.READY_TO_EXECUTE

    def mark_dispatched(self) -> None:
        now = timezone.now()
        self.dispatch_status = self.DispatchStatus.DISPATCHED
        self.execution_status = self.ExecutionStatus.EXECUTING
        self.dispatched_at = now
        self.last_attempt_at = now
        self.attempt_count += 1

    def mark_succeeded(self) -> None:
        now = timezone.now()
        self.dispatch_status = self.DispatchStatus.COMPLETED
        self.execution_status = self.ExecutionStatus.SUCCEEDED
        self.completed_at = now

    def mark_failed(self, code: str, message: str) -> None:
        self.dispatch_status = self.DispatchStatus.FAILED
        self.execution_status = self.ExecutionStatus.FAILED
        self.last_error_code = code
        self.last_error_message = message
