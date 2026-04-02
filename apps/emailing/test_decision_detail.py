from django.test import SimpleTestCase

from apps.emailing.decision_detail import (
    build_email_decision_context,
    resolve_email_trace,
)


class DummyEmail:
    def __init__(self, trace):
        self.id = 123
        self.subject = "Pricing question"
        self.sender = "client@example.com"
        self.rule_trace = trace


class EmailDecisionDetailTests(SimpleTestCase):
    def test_resolve_email_trace_reads_supported_attribute(self):
        trace = [
            {
                "rule": "pricing_interest_detected",
                "event_type": "rule_selection",
                "rule_selected": True,
                "selection_priority": 100,
                "is_final": True,
            },
            {
                "rule": "default_fallback",
                "event_type": "rule_discard_shadowed",
                "rule_discarded": True,
                "discard_reason": "shadowed_by_final_rule",
            },
            {
                "event_type": "final_effect",
                "final_effect": True,
                "final_matched": True,
                "matched_rules_count": 1,
            },
        ]
        email_obj = DummyEmail(trace)

        self.assertEqual(resolve_email_trace(email_obj), trace)

    def test_build_email_decision_context_exposes_ui_payload(self):
        trace = [
            {
                "rule": "pricing_interest_detected",
                "event_type": "rule_selection",
                "rule_selected": True,
                "selection_priority": 100,
                "is_final": True,
            },
            {
                "rule": "default_fallback",
                "event_type": "rule_discard_shadowed",
                "rule_discarded": True,
                "discard_reason": "shadowed_by_final_rule",
            },
            {
                "event_type": "final_effect",
                "final_effect": True,
                "final_matched": True,
                "matched_rules_count": 1,
            },
        ]
        email_obj = DummyEmail(trace)

        context = build_email_decision_context(email_obj)

        self.assertTrue(context["has_decision_trace"])
        self.assertEqual(context["trace"], trace)
        self.assertIn("selected_rules", context["decision_output"])
        self.assertIn("discarded_rules", context["decision_output"])
        self.assertIn("final_effect", context["decision_output"])
        self.assertIn("explanation", context["decision_output"])
        self.assertEqual(context["decision_output"]["selected_rules"][0]["rule"], "pricing_interest_detected")
