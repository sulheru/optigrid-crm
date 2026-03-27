from pathlib import Path

path = Path("apps/external_actions/services.py")
text = path.read_text()

import_line = "from apps.external_actions.dispatcher import dispatch_external_action_intent"

if import_line not in text:
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from apps.external_actions"):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    text = "\n".join(lines) + "\n"

old = """    return intent"""

new = """    # ---------------------------------------------------------
    # AUTO-DISPATCH (solo intents seguros)
    # ---------------------------------------------------------
    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        try:
            dispatch_external_action_intent(intent)
        except Exception:
            # no rompemos el flujo principal
            pass

    return intent"""

if old not in text:
    raise SystemExit("No se encontró el return intent esperado.")

text = text.replace(old, new)
path.write_text(text)

print("[ok] auto-dispatch para intents seguros activado")
