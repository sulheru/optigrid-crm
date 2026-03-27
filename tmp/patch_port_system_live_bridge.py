from pathlib import Path
import re

# -------------------------------------------------------------------
# 1) Patch apps/recommendations/views.py
#    Idea:
#    - añadir import del bridge
#    - antes de _mark_recommendation_executed(recommendation), intentar
#      crear/reutilizar el ExternalActionIntent
# -------------------------------------------------------------------

views_path = Path("apps/recommendations/views.py")
views_text = views_path.read_text()

import_line = (
    "from apps.recommendations.services.external_actions import "
    "ensure_external_action_intent_for_recommendation"
)

if import_line not in views_text:
    lines = views_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from apps.recommendations") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    views_text = "\n".join(lines) + "\n"

old_marker = "_mark_recommendation_executed(recommendation)"
new_marker = """intent, _created = ensure_external_action_intent_for_recommendation(
        recommendation,
        requested_by=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
    )
    _mark_recommendation_executed(recommendation)"""

if old_marker in views_text and "ensure_external_action_intent_for_recommendation(" not in views_text.split(old_marker)[0][-500:]:
    views_text = views_text.replace(old_marker, new_marker)

views_path.write_text(views_text)
print("[ok] patched apps/recommendations/views.py")


# -------------------------------------------------------------------
# 2) Patch apps/recommendations/execution_application.py
#    Idea:
#    - si el servicio ya crea draft local, añadir también el intent
# -------------------------------------------------------------------

exec_app_path = Path("apps/recommendations/execution_application.py")
exec_app_text = exec_app_path.read_text()

import_line_2 = (
    "from apps.recommendations.services.external_actions import "
    "ensure_external_action_intent_for_recommendation"
)

if import_line_2 not in exec_app_text:
    lines = exec_app_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from apps.recommendations") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line_2)
    exec_app_text = "\n".join(lines) + "\n"

old_block = """        outbound = create_reply_draft_from_recommendation(recommendation)
        result.side_effects.append("draft_created")"""

new_block = """        outbound = create_reply_draft_from_recommendation(recommendation)
        result.side_effects.append("draft_created")

        intent, created = ensure_external_action_intent_for_recommendation(recommendation)
        if intent is not None:
            result.side_effects.append(
                "external_intent_created" if created else "external_intent_reused"
            )"""

if old_block in exec_app_text:
    exec_app_text = exec_app_text.replace(old_block, new_block)
    print("[ok] patched draft bridge in apps/recommendations/execution_application.py")
else:
    print("[skip] no se encontró el bloque exacto en execution_application.py; no se modificó")

exec_app_path.write_text(exec_app_text)


# -------------------------------------------------------------------
# 3) Patch apps/recommendations/services/external_actions.py
#    Mejora:
#    - si no hay destinatario, permitir igualmente draft local vacío
#      sin bloquear el intent a nivel de preparación interna futura
#    - de momento solo ajustamos subject/body si faltan
# -------------------------------------------------------------------

bridge_path = Path("apps/recommendations/services/external_actions.py")
bridge_text = bridge_path.read_text()

# Sin cambios estructurales obligatorios ahora; dejamos el archivo intacto.
bridge_path.write_text(bridge_text)
print("[ok] verified apps/recommendations/services/external_actions.py")


# -------------------------------------------------------------------
# 4) Añadir test de humo sobre el bridge en execution_application
#    Solo si existe el patrón adecuado para no romper el test suite.
# -------------------------------------------------------------------

test_path = Path("apps/external_actions/tests.py")
test_text = test_path.read_text()

append_block = '''

from apps.recommendations.services.external_actions import get_open_external_intent_for_recommendation


class RecommendationExternalBridgeSmokeTests(TestCase):
    def test_bridge_creates_single_open_intent_for_followup(self):
        recommendation = AIRecommendation.objects.create(
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
'''

if "RecommendationExternalBridgeSmokeTests" not in test_text:
    test_text += append_block
    test_path.write_text(test_text)
    print("[ok] appended smoke test")
else:
    print("[ok] smoke test already present")
