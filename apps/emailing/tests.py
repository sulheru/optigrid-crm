from django.test import TestCase

from apps.emailing.services.inbound_decision_engine import build_inbound_decision
from apps.emailing.services.inbound_interpreter import interpret_inbound_email


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
