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
