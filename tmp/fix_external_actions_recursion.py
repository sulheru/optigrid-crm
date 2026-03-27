from pathlib import Path
import re

path = Path("apps/external_actions/services/core.py")
text = path.read_text()

# 1) Asegurar import con alias para no pisar el nombre local
plain_import = "from apps.external_actions.dispatcher import dispatch_external_action_intent"
alias_import = "from apps.external_actions.dispatcher import dispatch_external_action_intent as run_external_action_dispatch"

if plain_import in text and alias_import not in text:
    text = text.replace(plain_import, alias_import)

if alias_import not in text:
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from apps.external_actions") or line.startswith("from services.ports") or line.startswith("from django"):
            insert_at = i + 1
    lines.insert(insert_at, alias_import)
    text = "\n".join(lines) + "\n"

# 2) Cambiar solo las llamadas internas del create_* para usar el alias externo.
#    No tocamos la definición local de la función.
text = text.replace(
    "            dispatch_external_action_intent(intent)",
    "            run_external_action_dispatch(intent)",
)

text = text.replace(
    "            dispatch_external_action_intent(intent)\n        except Exception:",
    "            run_external_action_dispatch(intent)\n        except Exception:",
)

# 3) Si existe una función local dispatch_external_action_intent en core.py,
#    la convertimos en wrapper explícito sin autorecursión.
pattern = re.compile(
    r"@transaction\.atomic\s*\n"
    r"def dispatch_external_action_intent\(intent: ExternalActionIntent\):"
    r".*?"
    r"return intent, normalized",
    re.DOTALL,
)

wrapper = """@transaction.atomic
def dispatch_external_action_intent(intent: ExternalActionIntent):
    return run_external_action_dispatch(intent)
"""

if pattern.search(text):
    text = pattern.sub(wrapper, text)

# 4) Limpieza defensiva de cualquier autorecursión residual
text = text.replace(
    "    dispatch_external_action_intent(intent)\n",
    "    return run_external_action_dispatch(intent)\n",
)

path.write_text(text)
print("[ok] recursion fix applied to apps/external_actions/services/core.py")
