from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.emailing.models import (
    InboundDecision,
    InboundEmail,
    InboundInterpretation,
    OutboundEmail,
)
from apps.emailing.services.inbound_analysis_service import analyze_inbound_email
from apps.emailing.services.inbound_decision_apply_service import (
    apply_inbound_decision,
    dismiss_inbound_decision,
)
from apps.emailing.services.inbound_decision_engine import build_inbound_decision
from apps.emailing.services.inbound_interpreter import interpret_inbound_email
from apps.opportunities.models import Opportunity
from apps.tasks.models import CRMTask
from apps.tenancy.models import MailboxAccount, OperatingOrganization


class DummyOpportunity:
    id = 123


class DummyInbound:
    def __init__(self, reply_type, body="", opportunity=None):
        self.reply_type = reply_type
        self.body = body
        self.opportunity = opportunity


class InboundAnalysisServiceUnitTest(TestCase):
    def test_interested_maps_to_advance_opportunity(self):
        inbound = DummyInbound(
            reply_type="interested",
            body="We are interested. Let's talk this week.",
            opportunity=DummyOpportunity(),
        )

        interpretation = interpret_inbound_email(inbound)
        decision = build_inbound_decision(inbound, interpretation)

        self.assertEqual(interpretation.intent, "interested")
        self.assertEqual(interpretation.recommended_action, "advance_opportunity")
        self.assertEqual(interpretation.sentiment, "positive")
        self.assertEqual(interpretation.urgency, "high")
        self.assertEqual(decision.action_type, "advance_opportunity")
        self.assertTrue(decision.requires_approval)

    def test_not_now_maps_to_followup(self):
        inbound = DummyInbound(
            reply_type="not_now",
            body="Not now, maybe later.",
            opportunity=DummyOpportunity(),
        )

        interpretation = interpret_inbound_email(inbound)
        decision = build_inbound_decision(inbound, interpretation)

        self.assertEqual(interpretation.intent, "delay")
        self.assertEqual(interpretation.recommended_action, "schedule_followup")
        self.assertEqual(interpretation.sentiment, "neutral")
        self.assertEqual(interpretation.urgency, "low")
        self.assertEqual(decision.action_type, "schedule_followup")
        self.assertFalse(decision.requires_approval)

    def test_not_interested_maps_to_mark_lost(self):
        inbound = DummyInbound(
            reply_type="not_interested",
            body="No thanks, not interested.",
            opportunity=DummyOpportunity(),
        )

        interpretation = interpret_inbound_email(inbound)
        decision = build_inbound_decision(inbound, interpretation)

        self.assertEqual(interpretation.intent, "rejection")
        self.assertEqual(interpretation.recommended_action, "mark_lost")
        self.assertEqual(interpretation.sentiment, "negative")
        self.assertEqual(interpretation.urgency, "low")
        self.assertEqual(decision.action_type, "mark_lost")
        self.assertTrue(decision.requires_approval)


class ApplyInboundDecisionServiceTest(TestCase):
    def setUp(self):
        self.org = OperatingOrganization.objects.create(
            name="OptiGrid",
            primary_domain="optigrid.test",
        )
        self.mailbox = MailboxAccount.objects.create(
            operating_organization=self.org,
            email="inbox@optigrid.test",
            account_key="inbox_main",
            provider="embedded",
            display_name="Inbox Main",
        )
        self.opportunity = Opportunity.objects.create(
            title="Test Opportunity",
            company_name="ACME",
            stage="new",
        )

        self.inbound = InboundEmail.objects.create(
            opportunity=self.opportunity,
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            from_email="lead@example.com",
            subject="Interested in learning more",
            body="Please send more information.",
            status=InboundEmail.STATUS_NEW,
            reply_type=InboundEmail.REPLY_NEEDS_INFO,
            received_at=timezone.now(),
        )

        self.interpretation = InboundInterpretation.objects.create(
            inbound_email=self.inbound,
            intent=InboundInterpretation.INTENT_OBJECTION,
            urgency=InboundInterpretation.URGENCY_MEDIUM,
            sentiment=InboundInterpretation.SENTIMENT_NEUTRAL,
            recommended_action=InboundInterpretation.ACTION_SEND_INFORMATION,
            confidence=0.85,
            rationale="Needs more information",
            signals_json={"needs_info": True},
        )

    def test_inbound_email_requires_mailbox_account(self):
        with self.assertRaises(ValidationError):
            InboundEmail.objects.create(
                opportunity=self.opportunity,
                from_email="lead@example.com",
                subject="Missing canonical identity",
                body="Body",
                status=InboundEmail.STATUS_NEW,
                reply_type=InboundEmail.REPLY_NEEDS_INFO,
                received_at=timezone.now(),
            )

    def test_apply_schedule_followup_creates_task(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_SCHEDULE_FOLLOWUP,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Schedule a follow-up in a few days",
            payload_json={},
            requires_approval=False,
            score=72,
            priority="medium",
            risk_flags=[],
        )

        result = apply_inbound_decision(decision)

        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertIsNotNone(decision.applied_at)
        self.assertFalse(decision.applied_automatically)
        self.assertEqual(CRMTask.objects.count(), 1)
        self.assertIsNotNone(result["task_id"])

    def test_apply_send_information_creates_draft(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_SEND_INFORMATION,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Send company overview and next steps",
            payload_json={},
            requires_approval=True,
            score=70,
            priority="medium",
            risk_flags=["requires_approval"],
        )

        result = apply_inbound_decision(decision)

        decision.refresh_from_db()
        outbound = OutboundEmail.objects.get(id=result["outbound_id"])

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertEqual(outbound.status, OutboundEmail.STATUS_DRAFT)
        self.assertEqual(outbound.email_type, OutboundEmail.TYPE_FOLLOWUP)
        self.assertEqual(outbound.to_email, "lead@example.com")
        self.assertEqual(outbound.source_inbound_id, self.inbound.id)

    def test_apply_advance_opportunity_moves_stage(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_ADVANCE_OPPORTUNITY,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Advance opportunity to next stage",
            payload_json={},
            requires_approval=True,
            score=88,
            priority="high",
            risk_flags=["requires_approval", "sensitive_stage_change"],
        )

        result = apply_inbound_decision(decision)

        self.opportunity.refresh_from_db()
        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertEqual(self.opportunity.stage, "qualified")
        self.assertEqual(result["opportunity_stage"], "qualified")

    def test_apply_mark_lost(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_MARK_LOST,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Mark opportunity as lost",
            payload_json={},
            requires_approval=True,
            score=25,
            priority="low",
            risk_flags=["requires_approval", "negative_sentiment", "blocked_action"],
        )

        apply_inbound_decision(decision)

        self.opportunity.refresh_from_db()
        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertEqual(self.opportunity.stage, "lost")

    def test_dismiss_decision(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_SEND_CLARIFICATION,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Ask for clarification",
            payload_json={},
            requires_approval=True,
            score=45,
            priority="medium",
            risk_flags=["requires_approval"],
        )

        dismiss_inbound_decision(decision)
        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_DISMISSED)


@override_settings(
    INBOX_AUTO_APPLY_ENABLED=True,
    INBOX_AUTO_APPLY_SCORE_THRESHOLD=60,
    INBOX_AUTO_BLOCKED_ACTIONS=["mark_lost", "advance_opportunity"],
    INBOX_AUTO_BLOCK_ON_RISK_FLAGS=[
        "low_confidence",
        "unclear_intent",
        "negative_sentiment",
        "contradictory_signals",
        "requires_approval",
        "blocked_action",
        "sensitive_stage_change",
    ],
)
class AutomationLayerV3Test(TestCase):
    def setUp(self):
        self.org = OperatingOrganization.objects.create(
            name="OptiGrid",
            primary_domain="optigrid.test",
        )
        self.mailbox = MailboxAccount.objects.create(
            operating_organization=self.org,
            email="inbox@optigrid.test",
            account_key="inbox_main",
            provider="embedded",
            display_name="Inbox Main",
        )
        self.opportunity = Opportunity.objects.create(
            title="Automation Opportunity",
            company_name="ACME",
            stage="new",
        )

    def test_analyze_inbound_email_auto_applies_safe_decision(self):
        inbound = InboundEmail.objects.create(
            opportunity=self.opportunity,
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            from_email="lead@example.com",
            subject="Need more details",
            body="Please send more information about your services.",
            status=InboundEmail.STATUS_NEW,
            reply_type=InboundEmail.REPLY_NEEDS_INFO,
            received_at=timezone.now(),
        )

        result = analyze_inbound_email(inbound)

        decision = InboundDecision.objects.get(id=result["decision_id"])
        outbound = OutboundEmail.objects.get(source_inbound=inbound)

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertTrue(decision.applied_automatically)
        self.assertGreaterEqual(decision.score, 60)
        self.assertEqual(outbound.status, OutboundEmail.STATUS_DRAFT)

    def test_analyze_inbound_email_dedupes_existing_applied_decision(self):
        inbound = InboundEmail.objects.create(
            opportunity=self.opportunity,
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            from_email="lead@example.com",
            subject="Need more details",
            body="Please send more information about your services.",
            status=InboundEmail.STATUS_NEW,
            reply_type=InboundEmail.REPLY_NEEDS_INFO,
            received_at=timezone.now(),
        )

        first = analyze_inbound_email(inbound)
        second = analyze_inbound_email(inbound)

        self.assertEqual(first["decision_id"], second["decision_id"])
        self.assertEqual(
            InboundDecision.objects.filter(
                inbound_email=inbound,
                action_type=InboundDecision.ACTION_SEND_INFORMATION,
            ).count(),
            1,
        )
        self.assertEqual(
            OutboundEmail.objects.filter(source_inbound=inbound).count(),
            1,
        )

    def test_blocked_action_remains_manual(self):
        inbound = InboundEmail.objects.create(
            opportunity=self.opportunity,
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            from_email="lead@example.com",
            subject="We are interested",
            body="We are interested and would like to move forward.",
            status=InboundEmail.STATUS_NEW,
            reply_type=InboundEmail.REPLY_INTERESTED,
            received_at=timezone.now(),
        )

        result = analyze_inbound_email(inbound)
        decision = InboundDecision.objects.get(id=result["decision_id"])

        self.assertEqual(decision.action_type, InboundDecision.ACTION_ADVANCE_OPPORTUNITY)
        self.assertEqual(decision.status, InboundDecision.STATUS_SUGGESTED)
        self.assertFalse(decision.applied_automatically)
