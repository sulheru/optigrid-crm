from types import SimpleNamespace
from unittest.mock import patch

from django.http import Http404
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase

from apps.emailing.models import InboundEmail
from apps.emailing.views_decision import email_decision_detail


def _build_email_stub(email_id: int = 1) -> SimpleNamespace:
    return SimpleNamespace(
        id=email_id,
        subject="Decision trace test email",
        from_email="sender@example.com",
        received_at="2026-04-02 18:00:00",
        body="Hello from the decision trace test.",
        status="new",
        opportunity=SimpleNamespace(
            title="Pipeline Opportunity",
            stage="qualified",
        ),
        ai_interpretation=None,
        latest_decision=None,
        suggested_decision=None,
    )


def _build_decision_view_context(email_id: int = 1) -> dict:
    return {
        "email": _build_email_stub(email_id=email_id),
        "trace": {
            "events": [
                {
                    "event_type": "rule_selected",
                    "rule": "prepare_pricing_response",
                },
                {
                    "event_type": "rule_discarded",
                    "rule": "mark_lost_after_negative_signal",
                },
                {
                    "event_type": "final_effect",
                    "effect_type": "reply_strategy",
                    "payload": {"template": "pricing_response"},
                },
            ]
        },
        "trace_source": "rule_evaluation_log",
        "has_decision": True,
        "decision_output": {
            "selected_rules": [
                {"rule": "prepare_pricing_response"},
            ],
            "discarded_rules": [
                {"rule": "mark_lost_after_negative_signal"},
            ],
            "final_effect": {
                "effect_type": "reply_strategy",
                "payload": {"template": "pricing_response"},
            },
            "explanation": [
                "Rule prepare_pricing_response was selected.",
                "Rule mark_lost_after_negative_signal was discarded.",
                "Final effect is reply_strategy.",
            ],
        },
    }


class EmailDecisionDetailViewTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    @patch("apps.emailing.views_decision.get_email_decision_view")
    def test_email_decision_detail_renders_full_decision_output(self, mock_get_email_decision_view):
        mock_get_email_decision_view.return_value = _build_decision_view_context(email_id=11)

        request = self.factory.get("/inbox/11/decision/")
        response = email_decision_detail(request, email_id=11)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertIn("Decision Detail", content)
        self.assertIn("Decision trace test email", content)
        self.assertIn("Trace source: rule_evaluation_log", content)
        self.assertIn("Selected Rules", content)
        self.assertIn("prepare_pricing_response", content)
        self.assertIn("Discarded Rules", content)
        self.assertIn("mark_lost_after_negative_signal", content)
        self.assertIn("Final Effect", content)
        self.assertIn("reply_strategy", content)
        self.assertIn("Explanation", content)
        self.assertIn("Rule prepare_pricing_response was selected.", content)

        mock_get_email_decision_view.assert_called_once_with(11)

    @patch("apps.emailing.views_decision.get_email_decision_view")
    def test_email_decision_detail_renders_empty_state_when_trace_is_missing(self, mock_get_email_decision_view):
        mock_get_email_decision_view.return_value = {
            "email": _build_email_stub(email_id=12),
            "trace": None,
            "trace_source": None,
            "has_decision": False,
            "decision_output": {
                "selected_rules": [],
                "discarded_rules": [],
                "final_effect": None,
                "explanation": [
                    "No decision trace is available for this email yet.",
                ],
            },
        }

        request = self.factory.get("/inbox/12/decision/")
        response = email_decision_detail(request, email_id=12)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertIn("Decision Not Available", content)
        self.assertIn("No decision trace could be found for this email.", content)

        mock_get_email_decision_view.assert_called_once_with(12)

    @patch("apps.emailing.views_decision.get_email_decision_view")
    def test_email_decision_detail_raises_404_for_unknown_email(self, mock_get_email_decision_view):
        mock_get_email_decision_view.side_effect = InboundEmail.DoesNotExist

        request = self.factory.get("/inbox/999/decision/")

        with self.assertRaises(Http404):
            email_decision_detail(request, email_id=999)

        mock_get_email_decision_view.assert_called_once_with(999)


class InboxEmailCardDecisionLinkTests(TestCase):
    def test_inbox_email_card_contains_decision_detail_link_when_decision_exists(self):
        email = _build_email_stub(email_id=21)
        email.ai_interpretation = SimpleNamespace(
            intent="pricing_request",
            urgency="medium",
            recommended_action="Prepare pricing response",
            confidence=0.82,
            rationale="Contact explicitly asked about pricing.",
        )
        email.latest_decision = SimpleNamespace(
            priority="medium",
            applied_automatically=False,
            action_type="reply_strategy",
            summary="Prepare a pricing-oriented reply.",
            score=0.82,
            requires_approval=True,
            risk_flags=["manual_review"],
        )

        html = render_to_string("emailing/partials/inbox_email_card.html", {"email": email})

        self.assertIn("View decision", html)
        self.assertIn("/inbox/21/decision/", html)
        self.assertIn("Decision detail", html)

    def test_inbox_email_card_contains_decision_detail_link_when_no_latest_decision_exists(self):
        email = _build_email_stub(email_id=22)
        email.ai_interpretation = None
        email.latest_decision = None

        html = render_to_string("emailing/partials/inbox_email_card.html", {"email": email})

        self.assertIn("/inbox/22/decision/", html)
        self.assertIn("Open decision trace", html)
        self.assertIn("Decision detail", html)
