from django.test import SimpleTestCase

from apps.updates.decision_output import build_decision_output


class DecisionOutputLayerTests(SimpleTestCase):
    def test_build_decision_output_returns_expected_structure(self):
        trace = [
            {
                "rule": "create_followup_task",
                "event_type": "rule_selection",
                "rule_selected": True,
            },
            {
                "rule": "open_opportunity",
                "event_type": "rule_discard_condition_failed",
                "rule_discarded": True,
                "discard_reason": "condition_not_matched",
            },
            {
                "event_type": "final_effect",
                "final_effect": True,
                "final_matched": True,
                "matched_rules_count": 1,
            },
        ]

        output = build_decision_output(trace)

        self.assertEqual(
            set(output.keys()),
            {"selected_rules", "discarded_rules", "final_effect", "explanation"},
        )
        self.assertEqual(len(output["selected_rules"]), 1)
        self.assertEqual(len(output["discarded_rules"]), 1)
        self.assertIsInstance(output["explanation"], list)
        self.assertTrue(output["explanation"])

    def test_build_decision_output_is_deterministic_for_same_trace(self):
        trace = [
            {
                "rule": "mark_contact_redirected",
                "event_type": "rule_selection",
                "rule_selected": True,
            },
            {
                "rule": "create_manual_review",
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

        output_a = build_decision_output(trace)
        output_b = build_decision_output(trace)

        self.assertEqual(output_a, output_b)

    def test_build_decision_output_reuses_real_helper_shapes(self):
        trace = [
            {
                "rule": "prepare_pricing_response",
                "event_type": "rule_selection",
                "rule_selected": True,
            },
            {
                "rule": "create_followup_task",
                "event_type": "rule_discard_conflict",
                "rule_discarded": True,
                "discard_reason": "conflict",
            },
            {
                "event_type": "final_effect",
                "final_effect": True,
                "final_matched": True,
                "matched_rules_count": 1,
            },
        ]

        output = build_decision_output(trace)

        self.assertEqual(output["selected_rules"][0]["rule"], "prepare_pricing_response")
        self.assertEqual(output["discarded_rules"][0]["rule"], "create_followup_task")
        self.assertIsInstance(output["explanation"], list)
