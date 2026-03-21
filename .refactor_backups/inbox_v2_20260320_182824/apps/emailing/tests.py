# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/.refactor_backups/inbox_v2_20260320_182824/apps/emailing/tests.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.test import TestCase
from django.utils import timezone

from apps.emailing.models import (
    InboundDecision,
    InboundEmail,
    InboundInterpretation,
    OutboundEmail,
)
from apps.emailing.services.inbound_decision_apply_service import (
    apply_inbound_decision,
    dismiss_inbound_decision,
)
from apps.emailing.services.inbound_decision_engine import build_inbound_decision
from apps.emailing.services.inbound_interpreter import interpret_inbound_email
from apps.opportunities.models import Opportunity
from apps.tasks.models import CRMTask


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
        self.opportunity = Opportunity.objects.create(
            title="Test Opportunity",
            company_name="ACME",
            stage="new",
        )

        self.inbound = InboundEmail.objects.create(
            opportunity=self.opportunity,
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

    def test_apply_schedule_followup_creates_task(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_SCHEDULE_FOLLOWUP,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Schedule a follow-up in a few days",
            payload_json={},
            requires_approval=False,
        )

        result = apply_inbound_decision(decision)

        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertIsNotNone(decision.applied_at)
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
        )

        dismiss_inbound_decision(decision)
        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_DISMISSED)
