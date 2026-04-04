from __future__ import annotations

from unittest.mock import Mock, patch

from django.test import TestCase

from apps.emailing.services.mail_provider_service import prepare_provider_draft
from apps.providers.mail_runtime import resolve_mail_account_ref
from apps.recommendations.execution_engine import (
    build_execution_request_from_recommendation,
    execute_execution_request,
)
from apps.recommendations.models import AIRecommendation, ExecutionLog
from apps.tenancy.models import MailboxAccount, OperatingOrganization


class MailRuntimeResolutionTests(TestCase):
    def test_resolve_mail_account_ref_from_db_mailbox(self):
        org = OperatingOrganization.objects.create(name="OptiGrid", primary_domain="optigrid.test")
        mailbox = MailboxAccount.objects.create(
            operating_organization=org,
            email="sales@optigrid.test",
            account_key="sales_main",
            provider="embedded",
            display_name="Sales Main",
        )

        ref = resolve_mail_account_ref(mailbox)

        self.assertEqual(ref.provider, "embedded")
        self.assertEqual(ref.account_key, "sales_main")
        self.assertEqual(ref.mailbox, "sales@optigrid.test")
        self.assertEqual(ref.metadata["mailbox_account_id"], mailbox.id)
        self.assertEqual(ref.metadata["operating_organization_id"], org.id)


class ProviderDraftServiceTests(TestCase):
    def test_prepare_provider_draft_uses_explicit_mailbox_account(self):
        org = OperatingOrganization.objects.create(name="OptiGrid", primary_domain="optigrid.test")
        mailbox = MailboxAccount.objects.create(
            operating_organization=org,
            email="sales@optigrid.test",
            account_key="sales_main",
            provider="embedded",
            display_name="Sales Main",
        )

        fake_result = Mock(
            provider="embedded",
            account_key="sales_main",
            external_draft_id="dr_123",
            status="created",
            payload={"ok": True},
        )
        fake_provider = Mock()
        fake_provider.create_draft.return_value = fake_result

        with patch(
            "apps.emailing.services.mail_provider_service.get_mail_provider_by_key",
            return_value=fake_provider,
        ):
            result = prepare_provider_draft(
                subject="Hola",
                body_text="Texto",
                to=["cliente@example.com"],
                mailbox_account=mailbox,
            )

        fake_provider.create_draft.assert_called_once()
        call_kwargs = fake_provider.create_draft.call_args.kwargs
        self.assertEqual(call_kwargs["account"].account_key, "sales_main")
        self.assertEqual(call_kwargs["account"].mailbox, "sales@optigrid.test")
        self.assertEqual(result["external_draft_id"], "dr_123")


class ExecutionEngineTests(TestCase):
    def setUp(self):
        self.org = OperatingOrganization.objects.create(
            name="OptiGrid",
            primary_domain="optigrid.test",
        )
        self.mailbox = MailboxAccount.objects.create(
            operating_organization=self.org,
            email="sales@optigrid.test",
            account_key="sales_main",
            provider="embedded",
            display_name="Sales Main",
        )

    def test_build_execution_request_allows_missing_mailbox(self):
        recommendation = AIRecommendation.objects.create(
            operating_organization=self.org,
            mailbox_account=None,
            scope_type="inbound_email",
            scope_id="1",
            recommendation_type="reply_strategy",
            recommendation_text="Responder con borrador",
            confidence=0.91,
        )

        request = build_execution_request_from_recommendation(recommendation)

        self.assertEqual(request.action_type, "prepare_reply_draft")
        self.assertEqual(request.operating_organization_id, self.org.id)
        self.assertIsNone(request.mailbox_account_id)

    def test_execute_execution_request_prepares_provider_draft_and_marks_executed(self):
        recommendation = AIRecommendation.objects.create(
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            scope_type="inbound_email",
            scope_id="1",
            recommendation_type="reply_strategy",
            recommendation_text="Responder con borrador",
            confidence=0.91,
        )

        request = build_execution_request_from_recommendation(recommendation, actor="tester")

        outbound = Mock()
        outbound.id = 77
        outbound.subject = "Re: Información"
        outbound.body = "Aquí tienes la información."
        outbound.to_email = "cliente@example.com"
        outbound.operating_organization_id = None
        outbound.mailbox_account_id = None

        with patch(
            "apps.recommendations.execution_engine.create_reply_draft_from_recommendation",
            return_value=outbound,
        ), patch(
            "apps.recommendations.execution_engine.prepare_provider_draft",
            return_value={
                "provider": "embedded",
                "account_key": "sales_main",
                "external_draft_id": "dr_777",
                "provider_status": "created",
                "provider_payload": {"ok": True},
            },
        ) as prepare_mock:
            result = execute_execution_request(request, recommendation=recommendation)

        outbound.save.assert_called_once()
        prepare_mock.assert_called_once()
        self.assertEqual(result["status"], ExecutionLog.STATUS_COMPLETED)
        self.assertEqual(result["created_entities"]["outbound_email_id"], 77)
        self.assertEqual(result["provider_result"]["external_draft_id"], "dr_777")
        self.assertTrue(
            ExecutionLog.objects.filter(
                recommendation=recommendation,
                action_type="prepare_reply_draft",
                status=ExecutionLog.STATUS_COMPLETED,
            ).exists()
        )

        recommendation.refresh_from_db()
        self.assertEqual(recommendation.status, AIRecommendation.STATUS_EXECUTED)

    def test_execute_execution_request_is_idempotent(self):
        recommendation = AIRecommendation.objects.create(
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            scope_type="inbound_email",
            scope_id="1",
            recommendation_type="reply_strategy",
            recommendation_text="Responder con borrador",
            confidence=0.91,
        )

        request = build_execution_request_from_recommendation(recommendation, actor="tester")

        outbound = Mock()
        outbound.id = 88
        outbound.subject = "Re: Información"
        outbound.body = "Aquí tienes la información."
        outbound.to_email = "cliente@example.com"
        outbound.operating_organization_id = None
        outbound.mailbox_account_id = None

        with patch(
            "apps.recommendations.execution_engine.create_reply_draft_from_recommendation",
            return_value=outbound,
        ) as create_draft_mock, patch(
            "apps.recommendations.execution_engine.prepare_provider_draft",
            return_value={
                "provider": "embedded",
                "account_key": "sales_main",
                "external_draft_id": "dr_888",
                "provider_status": "created",
                "provider_payload": {"ok": True},
            },
        ) as prepare_mock:
            first = execute_execution_request(request, recommendation=recommendation)
            second = execute_execution_request(request, recommendation=recommendation)

        self.assertEqual(first["status"], ExecutionLog.STATUS_COMPLETED)
        self.assertTrue(second["idempotent_replay"])
        self.assertIn("execution_deduplicated", second["side_effects"])
        self.assertEqual(
            ExecutionLog.objects.filter(
                recommendation=recommendation,
                action_type="prepare_reply_draft",
            ).count(),
            1,
        )
        create_draft_mock.assert_called_once()
        prepare_mock.assert_called_once()

    def test_send_action_is_blocked_by_policy_and_logged(self):
        recommendation = AIRecommendation.objects.create(
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            scope_type="inbound_email",
            scope_id="1",
            recommendation_type="reply_strategy",
            recommendation_text="Responder con borrador",
            confidence=0.91,
        )

        request = build_execution_request_from_recommendation(recommendation, actor="tester")
        request.action_type = "send_reply"

        result = execute_execution_request(request, recommendation=recommendation)

        self.assertEqual(result["status"], ExecutionLog.STATUS_BLOCKED)
        self.assertIn("execution_blocked_by_policy", result["side_effects"])
        self.assertTrue(
            ExecutionLog.objects.filter(
                recommendation=recommendation,
                action_type="send_reply",
                status=ExecutionLog.STATUS_BLOCKED,
            ).exists()
        )
