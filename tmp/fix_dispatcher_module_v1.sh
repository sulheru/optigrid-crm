#!/usr/bin/env bash
set -euo pipefail

cat > apps/external_actions/dispatcher.py << 'PY'
from __future__ import annotations

from django.utils import timezone

from apps.external_actions.models import ExternalActionIntent


class ExternalActionDispatchError(Exception):
    pass


def dispatch_external_action_intent(intent: ExternalActionIntent) -> ExternalActionIntent:
    """
    Dispatcher V1:
    - aplica policy
    - actualiza lifecycle
    - NO ejecuta provider real aún
    """

    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_SEND:
        if not intent.approval_required:
            raise ExternalActionDispatchError(
                "EMAIL_SEND debe tener approval_required=True"
            )

        if intent.approval_status != ExternalActionIntent.ApprovalStatus.APPROVED:
            raise ExternalActionDispatchError(
                "EMAIL_SEND requiere aprobación antes de dispatch"
            )

    intent.dispatch_status = ExternalActionIntent.DispatchStatus.DISPATCHED
    intent.execution_status = ExternalActionIntent.ExecutionStatus.EXECUTING

    now = timezone.now()
    intent.dispatched_at = now
    intent.last_attempt_at = now
    intent.attempt_count += 1

    try:
        # V1: simulación controlada, sin provider real todavía
        intent.dispatch_status = ExternalActionIntent.DispatchStatus.COMPLETED
        intent.execution_status = ExternalActionIntent.ExecutionStatus.SUCCEEDED
        intent.completed_at = timezone.now()
        intent.last_error_code = ""
        intent.last_error_message = ""

    except Exception as e:
        intent.dispatch_status = ExternalActionIntent.DispatchStatus.FAILED
        intent.execution_status = ExternalActionIntent.ExecutionStatus.FAILED
        intent.last_error_message = str(e)
        intent.last_error_code = "dispatch_error"
        raise

    finally:
        intent.save()

    return intent
PY

cat > apps/external_actions/tests_dispatcher.py << 'PY'
from django.test import TestCase

from apps.external_actions.dispatcher import (
    ExternalActionDispatchError,
    dispatch_external_action_intent,
)
from apps.external_actions.models import ExternalActionIntent


class ExternalActionDispatcherTests(TestCase):
    def test_email_create_draft_dispatch_ok(self):
        intent = ExternalActionIntent.objects.create(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            payload={},
        )

        dispatch_external_action_intent(intent)
        intent.refresh_from_db()

        self.assertEqual(
            intent.execution_status,
            ExternalActionIntent.ExecutionStatus.SUCCEEDED,
        )
        self.assertEqual(
            intent.dispatch_status,
            ExternalActionIntent.DispatchStatus.COMPLETED,
        )

    def test_email_send_requires_approval(self):
        intent = ExternalActionIntent.objects.create(
            intent_type=ExternalActionIntent.IntentType.EMAIL_SEND,
            port_name="mail",
            approval_required=True,
            approval_status=ExternalActionIntent.ApprovalStatus.PENDING_APPROVAL,
            payload={},
        )

        with self.assertRaises(ExternalActionDispatchError):
            dispatch_external_action_intent(intent)

    def test_email_send_with_approval_ok(self):
        intent = ExternalActionIntent.objects.create(
            intent_type=ExternalActionIntent.IntentType.EMAIL_SEND,
            port_name="mail",
            approval_required=True,
            approval_status=ExternalActionIntent.ApprovalStatus.APPROVED,
            payload={},
        )

        dispatch_external_action_intent(intent)
        intent.refresh_from_db()

        self.assertEqual(
            intent.execution_status,
            ExternalActionIntent.ExecutionStatus.SUCCEEDED,
        )
        self.assertEqual(
            intent.dispatch_status,
            ExternalActionIntent.DispatchStatus.COMPLETED,
        )
PY

echo "[ok] dispatcher movido a apps/external_actions/dispatcher.py"
echo "[ok] tests_dispatcher corregido"
