from pathlib import Path

path = Path("apps/external_actions/tests.py")
text = path.read_text()

append = '''

from apps.recommendations.models import AIRecommendation
from apps.recommendations.services.external_actions import (
    ensure_external_action_intent_for_recommendation,
    recommendation_supports_external_intent,
)


class RecommendationExternalBridgeTests(TestCase):
    def test_followup_recommendation_supports_external_intent(self):
        recommendation = AIRecommendation.objects.create(
            recommendation_type="followup",
            title="Follow up with contact",
            content="Prepare a polite follow-up.",
            rationale="No reply in thread.",
            confidence=0.75,
            status="new",
        )
        self.assertTrue(recommendation_supports_external_intent(recommendation))

    def test_ensure_external_action_intent_for_followup_creates_mail_draft_intent(self):
        recommendation = AIRecommendation.objects.create(
            recommendation_type="followup",
            title="Follow up with contact",
            content="Prepare a polite follow-up.",
            rationale="No reply in thread.",
            confidence=0.75,
            status="new",
        )

        intent, created = ensure_external_action_intent_for_recommendation(recommendation)

        self.assertTrue(created)
        self.assertIsNotNone(intent)
        self.assertEqual(intent.recommendation, recommendation)
        self.assertEqual(intent.intent_type, ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT)
        self.assertEqual(intent.port_name, "mail")
        self.assertEqual(intent.provider, "m365")
        self.assertEqual(intent.execution_status, ExternalActionIntent.ExecutionStatus.READY_TO_EXECUTE)

    def test_ensure_external_action_intent_for_followup_is_idempotent_at_app_level(self):
        recommendation = AIRecommendation.objects.create(
            recommendation_type="followup",
            title="Follow up with contact",
            content="Prepare a polite follow-up.",
            rationale="No reply in thread.",
            confidence=0.75,
            status="new",
        )

        intent_1, created_1 = ensure_external_action_intent_for_recommendation(recommendation)
        intent_2, created_2 = ensure_external_action_intent_for_recommendation(recommendation)

        self.assertTrue(created_1)
        self.assertFalse(created_2)
        self.assertEqual(intent_1.pk, intent_2.pk)
'''
if "RecommendationExternalBridgeTests" in text:
    print("[ok] tests de bridge ya presentes")
else:
    path.write_text(text + append)
    print("[ok] tests de bridge añadidos")
