from django.test import TestCase

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services import create_external_action_intent
from services.ports.idempotency import build_intent_idempotency_key
from services.ports.policy import evaluate_policy_for_intent
from services.ports.router import get_port_router


class ExternalActionPolicyTests(TestCase):
    def test_email_send_requires_human_approval(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_SEND,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        decision = evaluate_policy_for_intent(intent)
        self.assertEqual(decision.decision, "require_approval")
        self.assertTrue(decision.requires_approval)
        self.assertEqual(decision.classification, ExternalActionIntent.PolicyClassification.CRITICAL)

    def test_email_create_draft_is_automatic(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        decision = evaluate_policy_for_intent(intent)
        self.assertEqual(decision.decision, "allow")
        self.assertFalse(decision.requires_approval)
        self.assertEqual(decision.classification, ExternalActionIntent.PolicyClassification.AUTOMATIC)


class ExternalActionServiceTests(TestCase):
    def test_create_intent_send_starts_pending_approval(self):
        intent = create_external_action_intent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_SEND,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        self.assertEqual(intent.approval_status, ExternalActionIntent.ApprovalStatus.PENDING_APPROVAL)
        self.assertEqual(intent.execution_status, ExternalActionIntent.ExecutionStatus.DRAFT)

    def test_create_intent_draft_is_ready(self):
        intent = create_external_action_intent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        self.assertEqual(intent.approval_status, ExternalActionIntent.ApprovalStatus.NOT_REQUIRED)
        self.assertEqual(intent.execution_status, ExternalActionIntent.ExecutionStatus.READY_TO_EXECUTE)

    def test_idempotency_key_is_stable_for_same_payload(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            target_ref_type="recommendation",
            target_ref_id="123",
            payload={"to": ["a@example.com"], "subject": "Hello", "body": "World"},
        )
        key1 = build_intent_idempotency_key(intent)
        key2 = build_intent_idempotency_key(intent)
        self.assertEqual(key1, key2)


class ExternalActionRouterTests(TestCase):
    def test_router_resolves_m365_mail_port(self):
        intent = ExternalActionIntent(
            intent_type=ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            port_name="mail",
            provider="m365",
            payload={"to": ["a@example.com"], "subject": "Hello"},
        )
        port = get_port_router().resolve(intent)
        self.assertEqual(port.adapter_key, "m365.mail")


from apps.recommendations.models import AIRecommendation
from apps.recommendations.services.external_actions import (
    ensure_external_action_intent_for_recommendation,
    get_open_external_intent_for_recommendation,
    recommendation_supports_external_intent,
)


def _make_recommendation(**overrides):
    field_names = {f.name for f in AIRecommendation._meta.get_fields() if getattr(f, "concrete", False)}

    payload = {}

    # Campo base esperado por el sistema actual
    if "recommendation_type" in field_names:
        payload["recommendation_type"] = overrides.get("recommendation_type", "followup")

    # Campos opcionales: solo si existen en el modelo real
    optional_candidates = {
        "title": overrides.get("title", "Follow up with contact"),
        "name": overrides.get("title", "Follow up with contact"),
        "summary": overrides.get("content", "Prepare a polite follow-up."),
        "content": overrides.get("content", "Prepare a polite follow-up."),
        "description": overrides.get("content", "Prepare a polite follow-up."),
        "message": overrides.get("content", "Prepare a polite follow-up."),
        "body": overrides.get("content", "Prepare a polite follow-up."),
        "rationale": overrides.get("rationale", "No reply in thread."),
        "reasoning": overrides.get("rationale", "No reply in thread."),
        "explanation": overrides.get("rationale", "No reply in thread."),
        "status": overrides.get("status", "new"),
        "confidence": overrides.get("confidence", 0.75),
        "metadata": overrides.get("metadata", {"target_email": "test@example.com"}),
        "payload": overrides.get("metadata", {"target_email": "test@example.com"}),
        "data": overrides.get("metadata", {"target_email": "test@example.com"}),
    }

    for key, value in optional_candidates.items():
        if key in field_names:
            payload[key] = value

    # Si el modelo exige campos adicionales no nulos sin default,
    # los rellenamos de forma conservadora.
    for field in AIRecommendation._meta.fields:
        if field.auto_created:
            continue
        if field.name in payload:
            continue
        if field.null:
            continue
        if field.has_default():
            continue
        if getattr(field, "blank", False):
            if field.get_internal_type() in {"CharField", "TextField"}:
                payload[field.name] = ""
                continue

        internal_type = field.get_internal_type()

        if internal_type in {"CharField", "TextField"}:
            payload[field.name] = ""
        elif internal_type in {"IntegerField", "BigIntegerField", "PositiveIntegerField", "SmallIntegerField"}:
            payload[field.name] = 0
        elif internal_type in {"FloatField", "DecimalField"}:
            payload[field.name] = 0
        elif internal_type == "BooleanField":
            payload[field.name] = False

    safe_overrides = {k: v for k, v in overrides.items() if k in field_names}
    payload.update(safe_overrides)
    return AIRecommendation.objects.create(**payload)


class RecommendationExternalBridgeTests(TestCase):
    def test_followup_recommendation_supports_external_intent(self):
        recommendation = _make_recommendation(
            recommendation_type="followup",
            title="Follow up with contact",
            content="Prepare a polite follow-up.",
            rationale="No reply in thread.",
            confidence=0.75,
            status="new",
        )
        self.assertTrue(recommendation_supports_external_intent(recommendation))

    def test_ensure_external_action_intent_for_followup_creates_mail_draft_intent(self):
        recommendation = _make_recommendation(
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
        recommendation = _make_recommendation(
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


from apps.recommendations.services.external_actions import get_open_external_intent_for_recommendation


class RecommendationExternalBridgeSmokeTests(TestCase):
    def test_bridge_creates_single_open_intent_for_followup(self):
        recommendation = _make_recommendation(
            recommendation_type="followup",
            title="Follow up with contact",
            content="Prepare a polite follow-up.",
            rationale="No reply in thread.",
            confidence=0.75,
            status="new",
        )

        intent_1, created_1 = ensure_external_action_intent_for_recommendation(recommendation)
        intent_2 = get_open_external_intent_for_recommendation(
            recommendation,
            ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
        )

        self.assertTrue(created_1)
        self.assertIsNotNone(intent_1)
        self.assertIsNotNone(intent_2)
        self.assertEqual(intent_1.pk, intent_2.pk)
