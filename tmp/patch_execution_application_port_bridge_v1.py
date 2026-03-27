from pathlib import Path
import re

path = Path("apps/recommendations/execution_application.py")
text = path.read_text()

import_line = (
    "from apps.recommendations.services.external_actions import "
    "ensure_external_action_intent_for_recommendation"
)

if import_line not in text:
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from apps.recommendations") or line.startswith("from apps.emailing") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    text = "\n".join(lines) + "\n"
    print("[ok] import añadido en execution_application.py")
else:
    print("[ok] import ya presente en execution_application.py")

patterns = [
    (
        r'(outbound\s*=\s*create_reply_draft_from_recommendation\(recommendation\)\n)'
        r'(\s*result\.side_effects\.append\("draft_created"\))',
        r'\1\2\n'
        r'        intent, created = ensure_external_action_intent_for_recommendation(recommendation)\n'
        r'        if intent is not None:\n'
        r'            result.side_effects.append(\n'
        r'                "external_intent_created" if created else "external_intent_reused"\n'
        r'            )'
    ),
    (
        r'(create_reply_draft_from_recommendation\(recommendation\)\n)',
        r'\1'
        r'        intent, created = ensure_external_action_intent_for_recommendation(recommendation)\n'
        r'        if intent is not None:\n'
        r'            result.side_effects.append(\n'
        r'                "external_intent_created" if created else "external_intent_reused"\n'
        r'            )\n'
    ),
]

patched = False
for pattern, replacement in patterns:
    new_text, count = re.subn(pattern, replacement, text, count=1)
    if count:
        text = new_text
        patched = True
        print("[ok] bloque principal parcheado en execution_application.py")
        break

if not patched:
    marker = "def execute_recommendation_service("
    if marker in text and "external_intent_created" not in text:
        idx = text.index(marker)
        func_text = text[idx:]
        insert_marker = 'result.side_effects.append("draft_created")'
        if insert_marker in func_text:
            text = text.replace(
                insert_marker,
                insert_marker
                + '\n        intent, created = ensure_external_action_intent_for_recommendation(recommendation)\n'
                + '        if intent is not None:\n'
                + '            result.side_effects.append(\n'
                + '                "external_intent_created" if created else "external_intent_reused"\n'
                + '            )',
                1,
            )
            patched = True
            print("[ok] parche alternativo aplicado en execution_application.py")

if not patched:
    print("[warn] no se pudo parchear automáticamente execution_application.py")

path.write_text(text)
