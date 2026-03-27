#!/usr/bin/env bash
set -euo pipefail

mkdir -p apps/recommendations/services

cat > apps/recommendations/services/__init__.py << 'EOF'
EOF

cat > apps/recommendations/services/external_actions.py << 'EOF'
from __future__ import annotations

from typing import Any

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services import create_external_action_intent


MAIL_DRAFT_RECOMMENDATION_TYPES = {
    "followup",
    "reply_strategy",
    "contact_strategy",
}


def recommendation_supports_external_intent(recommendation) -> bool:
    recommendation_type = getattr(recommendation, "recommendation_type", "") or ""
    return recommendation_type in MAIL_DRAFT_RECOMMENDATION_TYPES


def map_recommendation_to_external_intent_spec(recommendation) -> dict[str, Any] | None:
    recommendation_type = getattr(recommendation, "recommendation_type", "") or ""

    if recommendation_type in MAIL_DRAFT_RECOMMENDATION_TYPES:
        return {
            "intent_type": ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT,
            "port_name": "mail",
            "provider": "m365",
            "target_ref_type": "recommendation",
            "target_ref_id": str(getattr(recommendation, "pk", "") or ""),
        }

    return None


def build_mail_payload_from_recommendation(recommendation) -> dict[str, Any]:
    content = getattr(recommendation, "content", "") or ""
    rationale = getattr(recommendation, "rationale", "") or ""
    title = getattr(recommendation, "title", "") or ""
    recommendation_type = getattr(recommendation, "recommendation_type", "") or ""

    subject = title or f"AI draft for {recommendation_type}"
    body_parts = [part for part in [content, rationale] if part]
    body = "\n\n".join(body_parts).strip()

    payload = {
        "to": [],
        "cc": [],
        "bcc": [],
        "subject": subject[:255] if subject else f"AI draft for {recommendation_type}",
        "body": body,
        "source_recommendation_id": getattr(recommendation, "pk", None),
        "recommendation_type": recommendation_type,
    }

    contact_email = _extract_contact_email(recommendation)
    if contact_email:
        payload["to"] = [contact_email]

    return payload


def _extract_contact_email(recommendation) -> str | None:
    for attr in ("contact", "target_contact", "related_contact"):
        obj = getattr(recommendation, attr, None)
        if obj is not None:
            email = getattr(obj, "email", None)
            if email:
                return email

    for attr in ("email_to", "target_email", "recipient_email"):
        value = getattr(recommendation, attr, None)
        if value:
            return value

    metadata = getattr(recommendation, "metadata", None)
    if isinstance(metadata, dict):
        for key in ("email", "to", "recipient_email", "target_email"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def get_open_external_intent_for_recommendation(recommendation, intent_type: str):
    return (
        ExternalActionIntent.objects.filter(
            recommendation=recommendation,
            intent_type=intent_type,
        )
        .exclude(
            execution_status__in=[
                ExternalActionIntent.ExecutionStatus.SUCCEEDED,
                ExternalActionIntent.ExecutionStatus.SUPERSEDED,
            ]
        )
        .order_by("-created_at")
        .first()
    )


def ensure_external_action_intent_for_recommendation(recommendation, *, requested_by=None):
    spec = map_recommendation_to_external_intent_spec(recommendation)
    if not spec:
        return None, False

    existing = get_open_external_intent_for_recommendation(recommendation, spec["intent_type"])
    if existing is not None:
        return existing, False

    payload = build_mail_payload_from_recommendation(recommendation)

    intent = create_external_action_intent(
        intent_type=spec["intent_type"],
        port_name=spec["port_name"],
        provider=spec["provider"],
        payload=payload,
        source_kind=ExternalActionIntent.SourceKind.RECOMMENDATION,
        source_id=str(getattr(recommendation, "pk", "") or ""),
        recommendation=recommendation,
        requested_by=requested_by,
        target_ref_type=spec["target_ref_type"],
        target_ref_id=spec["target_ref_id"],
        rationale=getattr(recommendation, "rationale", "") or "",
        reason=f"Created from recommendation:{getattr(recommendation, 'recommendation_type', '')}",
        confidence=getattr(recommendation, "confidence", None),
    )
    return intent, True
EOF

cat > tmp/patch_external_actions_dispatch.py << 'EOF'
from pathlib import Path

path = Path("apps/external_actions/services.py")
text = path.read_text()

old = """    router = get_port_router()
    port = router.resolve(intent)
"""
new = """    router = get_port_router()
    try:
        port = router.resolve(intent)
    except LookupError as exc:
        intent.mark_blocked(str(exc))
        intent.save(update_fields=["execution_status", "last_error_code", "last_error_message", "updated_at"])
        return intent, None
"""

if old not in text:
    raise SystemExit("No se encontró el bloque esperado para router.resolve(intent).")

path.write_text(text.replace(old, new))
print("[ok] dispatch_external_action_intent ahora bloquea limpiamente si no hay adapter.")
EOF

python3 tmp/patch_external_actions_dispatch.py

cat > tmp/extend_external_actions_tests.py << 'EOF'
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
EOF

python3 tmp/extend_external_actions_tests.py

python3 manage.py test apps.external_actions
python3 manage.py check

echo
echo "[next] inspección automática del entrypoint real de execute:"
echo "rg -n \"def .*execute|execute_.*followup|execute_.*reply|execute_.*contact|source_recommendation|OutboundEmail|draft\" apps/recommendations apps/emailing apps/tasks services"
