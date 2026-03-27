from pathlib import Path
import re

path = Path("apps/external_actions/services/core.py")
text = path.read_text()

# 1. Eliminar bloque de auto-dispatch (try/except completo)
text = re.sub(
    r"\n\s*#?\s*auto-?dispatch.*?\n\s*try:\n\s*.*?run_external_action_dispatch\(intent\).*?\n\s*except Exception:.*?\n\s*.*?\n",
    "\n",
    text,
    flags=re.DOTALL
)

# 2. Eliminar llamadas directas residuales
text = text.replace("run_external_action_dispatch(intent)", "")

# 3. Asegurar estado correcto tras creación
if "execution_status" in text:
    text = re.sub(
        r"intent\.execution_status\s*=\s*ExternalActionIntent\.ExecutionStatus\.\w+",
        "intent.execution_status = ExternalActionIntent.ExecutionStatus.READY_TO_EXECUTE",
        text
    )

path.write_text(text)
print("[ok] autodispatch eliminado de create_external_action_intent")
