from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services.approval import approve_external_action_intent

User = get_user_model()


class ExternalActionApprovalTests(TestCase):
    def test_approval_sets_fields(self):
        user = User.objects.create(username="tester")

        intent = ExternalActionIntent.objects.create(
            intent_type=ExternalActionIntent.IntentType.EMAIL_SEND,
            port_name="mail",
            approval_required=True,
            approval_status=ExternalActionIntent.ApprovalStatus.PENDING_APPROVAL,
            payload={},
        )

        approve_external_action_intent(intent, user)

        intent.refresh_from_db()

        self.assertEqual(
            intent.approval_status,
            ExternalActionIntent.ApprovalStatus.APPROVED,
        )
        self.assertEqual(intent.approved_by, user)
        self.assertIsNotNone(intent.approved_at)
