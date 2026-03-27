#!/usr/bin/env bash
set -euo pipefail

mkdir -p apps/external_actions/migrations
mkdir -p services/ports
mkdir -p services/adapters/m365

cat > apps/external_actions/__init__.py << 'EOF'
EOF

cat > apps/external_actions/apps.py << 'EOF'
from django.apps import AppConfig


class ExternalActionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.external_actions"
    verbose_name = "External Actions"
EOF

cat > apps/external_actions/models.py << 'EOF'
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ExternalActionIntent(models.Model):
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
EOF

cat > apps/external_actions/admin.py << 'EOF'
from django.contrib import admin

from .models import ExternalActionIntent


@admin.register(ExternalActionIntent)
class ExternalActionIntentAdmin(admin.ModelAdmin):
    list_display = (
        "public_id",
        "intent_type",
        "port_name",
        "provider",
        "policy_classification",
        "approval_status",
        "execution_status",
        "dispatch_status",
        "created_at",
    )
    list_filter = (
        "intent_type",
        "port_name",
        "provider",
        "policy_classification",
        "approval_status",
        "execution_status",
        "dispatch_status",
    )
    search_fields = (
        "public_id",
        "idempotency_key",
        "target_ref_type",
        "target_ref_id",
        "source_id",
        "last_error_code",
        "last_error_message",
    )
    readonly_fields = (
        "public_id",
        "created_at",
        "updated_at",
        "approved_at",
        "last_attempt_at",
        "dispatched_at",
        "completed_at",
    )
EOF

cat > apps/external_actions/services.py << 'EOF'
from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.external_actions.models import ExternalActionIntent
from services.ports.idempotency.py import build_intent_idempotency_key
from services.ports.policy import evaluate_policy_for_intent
from services.ports.router import get_port_router


@transaction.atomic
def create_external_action_intent(
    *,
    intent_type: str,
    port_name: str,
    payload: dict[str, Any],
    provider: str = "m365",
    source_kind: str = ExternalActionIntent.SourceKind.RECOMMENDATION,
    source_id: str = "",
    recommendation=None,
    task=None,
    requested_by=None,
    target_ref_type: str = "",
    target_ref_id: str = "",
    rationale: str = "",
    reason: str = "",
    confidence=None,
) -> ExternalActionIntent:
    intent = ExternalActionIntent.objects.create(
        intent_type=intent_type,
        port_name=port_name,
        provider=provider,
        source_kind=source_kind,
        source_id=source_id,
        recommendation=recommendation,
        task=task,
        requested_by=requested_by,
        target_ref_type=target_ref_type,
        target_ref_id=target_ref_id,
        payload=payload or {},
        rationale=rationale,
        reason=reason,
        confidence=confidence,
    )
    intent.idempotency_key = build_intent_idempotency_key(intent)
    decision = evaluate_policy_for_intent(intent)
    intent.policy_classification = decision.classification
    intent.approval_required = decision.requires_approval

    if decision.decision == "block":
        intent.mark_blocked("; ".join(decision.reasons) or "Blocked by policy.")
    elif decision.decision == "require_approval":
        intent.mark_pending_approval()
    else:
        intent.approval_status = ExternalActionIntent.ApprovalStatus.NOT_REQUIRED
        intent.mark_ready()

    intent.save()
    return intent


@transaction.atomic
def approve_external_action_intent(intent: ExternalActionIntent, *, approved_by=None) -> ExternalActionIntent:
    intent.mark_approved(user=approved_by)
    intent.mark_ready()
    intent.save(update_fields=[
        "approval_required",
        "approval_status",
        "approved_by",
        "approved_at",
        "dispatch_status",
        "execution_status",
        "updated_at",
    ])
    return intent


@transaction.atomic
def dispatch_external_action_intent(intent: ExternalActionIntent):
    if intent.requires_human_approval() and intent.approval_status != ExternalActionIntent.ApprovalStatus.APPROVED:
        intent.mark_blocked("Intent requires explicit human approval before dispatch.")
        intent.save(update_fields=["execution_status", "last_error_code", "last_error_message", "updated_at"])
        return intent, None

    router = get_port_router()
    port = router.resolve(intent)

    validation = port.validate(intent)
    if not validation.ok:
        intent.mark_blocked("; ".join(validation.errors) or "Validation failed.")
        intent.save(update_fields=["execution_status", "last_error_code", "last_error_message", "updated_at"])
        return intent, None

    prepared = port.prepare(intent)
    intent.normalized_preview = prepared.preview or {}
    intent.adapter_key = port.adapter_key
    intent.mark_dispatched()
    intent.save(update_fields=[
        "normalized_preview",
        "adapter_key",
        "dispatch_status",
        "execution_status",
        "dispatched_at",
        "last_attempt_at",
        "attempt_count",
        "updated_at",
    ])

    provider_result = port.execute(prepared)
    normalized = port.normalize_result(provider_result)

    if normalized.status == "succeeded":
        intent.mark_succeeded()
        intent.last_error_code = ""
        intent.last_error_message = ""
        if normalized.raw:
            intent.normalized_preview = normalized.raw
    else:
        intent.mark_failed(
            normalized.error_code or "provider_failed",
            normalized.summary or normalized.error_code or "Provider execution failed.",
        )

    intent.save()
    return intent, normalized
EOF

cat > apps/external_actions/tests.py << 'EOF'
from django.test import TestCase

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services import create_external_action_intent
from services.ports.idempotency import build_intent_idempotency_key
from services.ports.policy import evaluate_policy_for_intent
from services.ports.router import get_port_router


class ExternalActionPolicyTests(TestCase):
    def test_email_send_requires_human_approval(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_SEND,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        decision = evaluate_policy_for_intent(intent)
        self.assertEqual(decision.decision, "require_approval")
        self.assertTrue(decision.requires_approval)
        self.assertEqual(decision.classification, ExternalActionIntent.PolicyClassification.CRITICAL)

    def test_email_create_draft_is_automatic(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        decision = evaluate_policy_for_intent(intent)
        self.assertEqual(decision.decision, "allow")
        self.assertFalse(decision.requires_approval)
        self.assertEqual(decision.classification, ExternalActionIntent.PolicyClassification.AUTOMATIC)


class ExternalActionServiceTests(TestCase):
    def test_create_intent_send_starts_pending_approval(self):
        intent = create_external_action_intent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_SEND,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        self.assertEqual(intent.approval_status, ExternalActionIntent.ApprovalStatus.PENDING_APPROVAL)
        self.assertEqual(intent.execution_status, ExternalActionIntent.ExecutionStatus.DRAFT)

    def test_create_intent_draft_is_ready(self):
        intent = create_external_action_intent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        self.assertEqual(intent.approval_status, ExternalActionIntent.ApprovalStatus.NOT_REQUIRED)
        self.assertEqual(intent.execution_status, ExternalActionIntent.ExecutionStatus.READY_TO_EXECUTE)

    def test_idempotency_key_is_stable_for_same_payload(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            target_ref_type="recommendation",
            target_ref_id="123",
            payload={"to": ["a@example.com"], "subject": "Hello", "body": "World"},
        )
        key1 = build_intent_idempotency_key(intent)
        key2 = build_intent_idempotency_key(intent)
        self.assertEqual(key1, key2)


class ExternalActionRouterTests(TestCase):
    def test_router_resolves_m365_mail_port(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        port = get_port_router().resolve(intent)
        self.assertEqual(port.adapter_key, "m365.mail")
EOF

cat > apps/external_actions/migrations/__init__.py << 'EOF'
EOF

cat > apps/external_actions/migrations/0001_initial.py << 'EOF'
# Generated manually for PORT SYSTEM V1 foundation.
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recommendations", "0003_airecommendation_source"),
        ("tasks", "0004_crmtask_is_revoked"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExternalActionIntent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("intent_type", models.CharField(choices=[
                    ("email.create_draft", "Email: Create Draft"),
                    ("email.send", "Email: Send"),
                    ("calendar.create_event", "Calendar: Create Event"),
                    ("calendar.update_event", "Calendar: Update Event"),
                ], max_length=64)),
                ("port_name", models.CharField(max_length=32)),
                ("adapter_key", models.CharField(blank=True, default="", max_length=64)),
                ("provider", models.CharField(blank=True, default="", max_length=32)),
                ("target_ref_type", models.CharField(blank=True, default="", max_length=64)),
                ("target_ref_id", models.CharField(blank=True, default="", max_length=64)),
                ("source_kind", models.CharField(choices=[
                    ("recommendation", "Recommendation"),
                    ("task", "Task"),
                    ("chat", "Chat"),
                    ("workflow", "Workflow"),
                    ("system_rule", "System Rule"),
                    ("user_action", "User Action"),
                ], default="recommendation", max_length=32)),
                ("source_id", models.CharField(blank=True, default="", max_length=64)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("normalized_preview", models.JSONField(blank=True, default=dict)),
                ("policy_classification", models.CharField(choices=[
                    ("automatic", "Automatic"),
                    ("reviewable", "Reviewable"),
                    ("critical", "Critical"),
                ], default="reviewable", max_length=16)),
                ("approval_required", models.BooleanField(default=False)),
                ("approval_status", models.CharField(choices=[
                    ("not_required", "Not Required"),
                    ("pending_approval", "Pending Approval"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("expired", "Expired"),
                ], default="not_required", max_length=24)),
                ("dispatch_status", models.CharField(choices=[
                    ("not_dispatched", "Not Dispatched"),
                    ("ready", "Ready"),
                    ("dispatched", "Dispatched"),
                    ("acknowledged", "Acknowledged"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                    ("cancelled", "Cancelled"),
                ], default="not_dispatched", max_length=24)),
                ("execution_status", models.CharField(choices=[
                    ("draft", "Draft"),
                    ("validated", "Validated"),
                    ("blocked", "Blocked"),
                    ("dry_run_ready", "Dry Run Ready"),
                    ("ready_to_execute", "Ready To Execute"),
                    ("executing", "Executing"),
                    ("succeeded", "Succeeded"),
                    ("failed", "Failed"),
                    ("superseded", "Superseded"),
                ], default="draft", max_length=24)),
                ("idempotency_key", models.CharField(blank=True, db_index=True, default="", max_length=255)),
                ("idempotency_scope", models.CharField(blank=True, default="provider_account", max_length=32)),
                ("risk_score", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("reason", models.TextField(blank=True, default="")),
                ("rationale", models.TextField(blank=True, default="")),
                ("confidence", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("dry_run_supported", models.BooleanField(default=True)),
                ("last_error_code", models.CharField(blank=True, default="", max_length=64)),
                ("last_error_message", models.TextField(blank=True, default="")),
                ("attempt_count", models.PositiveIntegerField(default=0)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("last_attempt_at", models.DateTimeField(blank=True, null=True)),
                ("dispatched_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_external_action_intents", to=settings.AUTH_USER_MODEL)),
                ("recommendation", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_action_intents", to="recommendations.airecommendation")),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="requested_external_action_intents", to=settings.AUTH_USER_MODEL)),
                ("task", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_action_intents", to="tasks.crmtask")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["intent_type"], name="external_ac_intent__f9bc7f_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["port_name"], name="external_ac_port_na_45ece4_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["provider"], name="external_ac_provider_56f7fc_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["approval_status"], name="external_ac_approval_563470_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["execution_status"], name="external_ac_executi_5046f5_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["dispatch_status"], name="external_ac_dispatch_4bfbc3_idx"),
        ),
    ]
EOF

cat > services/ports/__init__.py << 'EOF'
EOF

cat > services/ports/types.py << 'EOF'
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PreparedAction:
    provider_payload: dict[str, Any]
    preview: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderResult:
    status: str
    provider_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool = False


@dataclass(slots=True)
class NormalizedExternalResult:
    status: str
    external_ref: str | None = None
    provider_id: str | None = None
    summary: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False
    error_code: str | None = None


@dataclass(slots=True)
class PolicyDecision:
    decision: str
    classification: str
    reasons: list[str] = field(default_factory=list)
    requires_approval: bool = False
    policy_snapshot: dict[str, Any] = field(default_factory=dict)
EOF

cat > services/ports/contracts.py << 'EOF'
from __future__ import annotations

from abc import ABC, abstractmethod

from services.ports.types import (
    NormalizedExternalResult,
    PreparedAction,
    ProviderResult,
    ValidationResult,
)


class ExternalPort(ABC):
    adapter_key: str = ""
    port_name: str = ""
    provider: str = ""

    @abstractmethod
    def validate(self, intent) -> ValidationResult:
        raise NotImplementedError

    @abstractmethod
    def prepare(self, intent) -> PreparedAction:
        raise NotImplementedError

    @abstractmethod
    def dry_run(self, intent) -> NormalizedExternalResult:
        raise NotImplementedError

    @abstractmethod
    def execute(self, prepared_action: PreparedAction) -> ProviderResult:
        raise NotImplementedError

    @abstractmethod
    def normalize_result(self, provider_result: ProviderResult) -> NormalizedExternalResult:
        raise NotImplementedError

    @abstractmethod
    def compute_idempotency(self, intent) -> str:
        raise NotImplementedError
EOF

cat > services/ports/idempotency.py << 'EOF'
from __future__ import annotations

import hashlib
import json


def _stable_json(data) -> str:
    return json.dumps(data or {}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_intent_idempotency_key(intent) -> str:
    semantic_fingerprint = hashlib.sha256(
        _stable_json(
            {
                "provider": getattr(intent, "provider", ""),
                "payload": getattr(intent, "payload", {}),
                "target_ref_type": getattr(intent, "target_ref_type", ""),
                "target_ref_id": getattr(intent, "target_ref_id", ""),
            }
        ).encode("utf-8")
    ).hexdigest()[:24]

    return "|".join(
        [
            getattr(intent, "intent_type", ""),
            f"{getattr(intent, 'target_ref_type', '')}:{getattr(intent, 'target_ref_id', '')}",
            semantic_fingerprint,
            "v1",
        ]
    )
EOF

cat > services/ports/policy.py << 'EOF'
from __future__ import annotations

from apps.external_actions.models import ExternalActionIntent
from services.ports.types import PolicyDecision


def evaluate_policy_for_intent(intent) -> PolicyDecision:
    reasons: list[str] = []

    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_SEND:
        reasons.append("HARD RULE: email.send always requires explicit human approval.")
        return PolicyDecision(
            decision="require_approval",
            classification=ExternalActionIntent.PolicyClassification.CRITICAL,
            reasons=reasons,
            requires_approval=True,
            policy_snapshot={"hard_rule": "email_send_human_approval_required"},
        )

    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        return PolicyDecision(
            decision="allow",
            classification=ExternalActionIntent.PolicyClassification.AUTOMATIC,
            reasons=["Draft creation is allowed automatically."],
            requires_approval=False,
            policy_snapshot={"rule": "draft_creation_allowed"},
        )

    if intent.intent_type in {
        ExternalActionIntent.IntentType.CALENDAR_CREATE_EVENT,
        ExternalActionIntent.IntentType.CALENDAR_UPDATE_EVENT,
    }:
        return PolicyDecision(
            decision="require_approval",
            classification=ExternalActionIntent.PolicyClassification.REVIEWABLE,
            reasons=["Calendar actions are reviewable by default in V1."],
            requires_approval=True,
            policy_snapshot={"rule": "calendar_reviewable_default"},
        )

    return PolicyDecision(
        decision="block",
        classification=ExternalActionIntent.PolicyClassification.CRITICAL,
        reasons=[f"Unsupported intent_type: {intent.intent_type}"],
        requires_approval=False,
        policy_snapshot={"rule": "unsupported_intent_type"},
    )
EOF

cat > services/ports/registry.py << 'EOF'
from __future__ import annotations

from typing import Dict

from services.adapters.m365.calendar import M365CalendarPort
from services.adapters.m365.mail import M365MailPort

_PORTS: Dict[str, object] = {}


def register_port(port) -> None:
    _PORTS[port.adapter_key] = port


def get_registered_ports() -> dict[str, object]:
    return dict(_PORTS)


def register_default_ports() -> None:
    if _PORTS:
        return
    register_port(M365MailPort())
    register_port(M365CalendarPort())
EOF

cat > services/ports/router.py << 'EOF'
from __future__ import annotations

from services.ports.registry import get_registered_ports, register_default_ports


class PortRouter:
    def __init__(self) -> None:
        register_default_ports()

    def resolve(self, intent):
        registered = get_registered_ports()

        if getattr(intent, "adapter_key", ""):
            adapter_key = intent.adapter_key
            if adapter_key not in registered:
                raise LookupError(f"Adapter not registered: {adapter_key}")
            return registered[adapter_key]

        provider = getattr(intent, "provider", "") or "m365"
        port_name = getattr(intent, "port_name", "")

        candidate_key = f"{provider}.{port_name}"
        if candidate_key in registered:
            return registered[candidate_key]

        raise LookupError(f"No adapter registered for provider={provider} port={port_name}")


_router = PortRouter()


def get_port_router() -> PortRouter:
    return _router
EOF

cat > services/adapters/__init__.py << 'EOF'
EOF

cat > services/adapters/m365/__init__.py << 'EOF'
EOF

cat > services/adapters/m365/mail.py << 'EOF'
from __future__ import annotations

from services.ports.contracts import ExternalPort
from services.ports.idempotency import build_intent_idempotency_key
from services.ports.types import (
    NormalizedExternalResult,
    PreparedAction,
    ProviderResult,
    ValidationResult,
)


class M365MailPort(ExternalPort):
    adapter_key = "m365.mail"
    port_name = "mail"
    provider = "m365"

    def validate(self, intent) -> ValidationResult:
        payload = intent.payload or {}
        errors: list[str] = []

        if intent.intent_type not in {"email.create_draft", "email.send"}:
            errors.append(f"Unsupported mail intent: {intent.intent_type}")

        recipients = payload.get("to") or []
        if not recipients:
            errors.append("payload.to is required")

        if not payload.get("subject"):
            errors.append("payload.subject is required")

        return ValidationResult(ok=not errors, errors=errors)

    def prepare(self, intent) -> PreparedAction:
        payload = intent.payload or {}
        preview = {
            "type": intent.intent_type,
            "to": payload.get("to", []),
            "cc": payload.get("cc", []),
            "bcc": payload.get("bcc", []),
            "subject": payload.get("subject", ""),
            "body_preview": (payload.get("body", "") or "")[:500],
        }
        return PreparedAction(provider_payload=payload, preview=preview)

    def dry_run(self, intent) -> NormalizedExternalResult:
        prepared = self.prepare(intent)
        return NormalizedExternalResult(
            status="dry_run",
            summary="Dry run completed successfully.",
            raw=prepared.preview,
        )

    def execute(self, prepared_action: PreparedAction) -> ProviderResult:
        # Slice V1:
        # - create_draft queda implementado como provider-ready payload
        # - send queda disponible para ejecución real solo cuando se conecte el provider
        payload = prepared_action.provider_payload or {}

        if payload.get("__simulate_failure__"):
            return ProviderResult(
                status="failed",
                error_code="simulated_failure",
                error_message="Simulated provider failure.",
                retryable=False,
            )

        return ProviderResult(
            status="succeeded",
            provider_id="m365-placeholder",
            raw={
                "provider": "m365",
                "adapter": self.adapter_key,
                "provider_payload": payload,
                "mode": "provider_ready",
            },
        )

    def normalize_result(self, provider_result: ProviderResult) -> NormalizedExternalResult:
        if provider_result.status == "succeeded":
            return NormalizedExternalResult(
                status="succeeded",
                provider_id=provider_result.provider_id,
                summary="Mail action accepted by adapter.",
                raw=provider_result.raw,
            )

        return NormalizedExternalResult(
            status="failed",
            provider_id=provider_result.provider_id,
            summary=provider_result.error_message or "Mail action failed.",
            raw=provider_result.raw,
            retryable=provider_result.retryable,
            error_code=provider_result.error_code,
        )

    def compute_idempotency(self, intent) -> str:
        return build_intent_idempotency_key(intent)
EOF

cat > services/adapters/m365/calendar.py << 'EOF'
from __future__ import annotations

from services.ports.contracts import ExternalPort
from services.ports.idempotency import build_intent_idempotency_key
from services.ports.types import (
    NormalizedExternalResult,
    PreparedAction,
    ProviderResult,
    ValidationResult,
)


class M365CalendarPort(ExternalPort):
    adapter_key = "m365.calendar"
    port_name = "calendar"
    provider = "m365"

    def validate(self, intent) -> ValidationResult:
        payload = intent.payload or {}
        errors: list[str] = []

        if intent.intent_type not in {"calendar.create_event", "calendar.update_event"}:
            errors.append(f"Unsupported calendar intent: {intent.intent_type}")

        if not payload.get("subject"):
            errors.append("payload.subject is required")

        if not payload.get("start"):
            errors.append("payload.start is required")

        if not payload.get("end"):
            errors.append("payload.end is required")

        return ValidationResult(ok=not errors, errors=errors)

    def prepare(self, intent) -> PreparedAction:
        payload = intent.payload or {}
        preview = {
            "type": intent.intent_type,
            "subject": payload.get("subject", ""),
            "start": payload.get("start"),
            "end": payload.get("end"),
            "attendees": payload.get("attendees", []),
            "location": payload.get("location", ""),
        }
        return PreparedAction(provider_payload=payload, preview=preview)

    def dry_run(self, intent) -> NormalizedExternalResult:
        prepared = self.prepare(intent)
        return NormalizedExternalResult(
            status="dry_run",
            summary="Calendar dry run completed successfully.",
            raw=prepared.preview,
        )

    def execute(self, prepared_action: PreparedAction) -> ProviderResult:
        payload = prepared_action.provider_payload or {}
        return ProviderResult(
            status="succeeded",
            provider_id="m365-calendar-placeholder",
            raw={
                "provider": "m365",
                "adapter": self.adapter_key,
                "provider_payload": payload,
                "mode": "provider_ready",
            },
        )

    def normalize_result(self, provider_result: ProviderResult) -> NormalizedExternalResult:
        if provider_result.status == "succeeded":
            return NormalizedExternalResult(
                status="succeeded",
                provider_id=provider_result.provider_id,
                summary="Calendar action accepted by adapter.",
                raw=provider_result.raw,
            )

        return NormalizedExternalResult(
            status="failed",
            provider_id=provider_result.provider_id,
            summary=provider_result.error_message or "Calendar action failed.",
            raw=provider_result.raw,
            retryable=provider_result.retryable,
            error_code=provider_result.error_code,
        )

    def compute_idempotency(self, intent) -> str:
        return build_intent_idempotency_key(intent)
EOF

cat > tmp/patch_settings_external_actions.py << 'EOF'
from pathlib import Path

settings_path = Path("config/settings.py")
text = settings_path.read_text()

if "apps.external_actions" in text:
    print("[ok] apps.external_actions already present")
    raise SystemExit(0)

needle = "INSTALLED_APPS = ["
idx = text.find(needle)
if idx == -1:
    raise SystemExit("Could not find INSTALLED_APPS in config/settings.py")

insert_at = idx + len(needle)
replacement = needle + "\n    'apps.external_actions',"
text = text[:idx] + replacement + text[insert_at:]

settings_path.write_text(text)
print("[ok] added apps.external_actions to config/settings.py")
EOF

python3 tmp/patch_settings_external_actions.py

echo "[ok] PORT SYSTEM V1 foundation files created"
