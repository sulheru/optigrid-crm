from django.test import TestCase

from .conditions import evaluate_condition
from .rule_engine import (
    evaluate_rules,
    get_selected_rules,
    get_discarded_rules,
    get_final_effect,
)


class DeclarativeConditionsTests(TestCase):
    def test_always_true_condition(self):
        self.assertTrue(
            evaluate_condition({"type": "always_true"}, {})
        )

    def test_inference_exists_condition_true(self):
        context = {
            "inferences": ["pricing_interest_signal"]
        }
        condition = {
            "type": "inference_exists",
            "params": {"inference_type": "pricing_interest_signal"},
        }
        self.assertTrue(evaluate_condition(condition, context))

    def test_inference_exists_condition_false(self):
        context = {
            "inferences": ["other_signal"]
        }
        condition = {
            "type": "inference_exists",
            "params": {"inference_type": "pricing_interest_signal"},
        }
        self.assertFalse(evaluate_condition(condition, context))


class RuleEngineDeclarativeTests(TestCase):
    def test_rule_engine_matches_final_rule(self):
        rules = [
            {
                "name": "pricing_interest_detected",
                "priority": 100,
                "outcome": "final",
                "conditions": [
                    {
                        "type": "inference_exists",
                        "params": {"inference_type": "pricing_interest_signal"},
                    }
                ],
                "proposal": {
                    "proposal_type": "prepare_pricing_response",
                },
            },
            {
                "name": "default_fallback",
                "priority": 0,
                "outcome": "fallback",
                "conditions": [{"type": "always_true"}],
                "proposal": {
                    "proposal_type": "review_manually",
                },
            },
        ]

        matched, trace = evaluate_rules(
            rules,
            {"inferences": ["pricing_interest_signal"]},
        )

        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0]["proposal"]["proposal_type"],
            "prepare_pricing_response",
        )


class RuleTraceV24HelpersTests(TestCase):
    def test_helpers_extract_information(self):
        rules = [
            {
                "name": "rule_a",
                "priority": 10,
                "conditions": [{"type": "always_true"}],
                "proposal": {"proposal_type": "a"},
            },
            {
                "name": "rule_b",
                "priority": 5,
                "conditions": [{"type": "always_true"}],
                "proposal": {"proposal_type": "a"},  # duplicado
            },
        ]

        matched, trace = evaluate_rules(rules, {"inferences": []})

        selected = get_selected_rules(trace)
        discarded = get_discarded_rules(trace)
        final = get_final_effect(trace)

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0], "rule_a")

        self.assertTrue(len(discarded) >= 1)
        self.assertIn("rule_b", [d["rule"] for d in discarded])

        self.assertTrue(final["final_effect"])
