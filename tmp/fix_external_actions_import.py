from pathlib import Path

path = Path("apps/external_actions/services.py")
text = path.read_text()

old = "from services.ports.idempotency.py import build_intent_idempotency_key"
new = "from services.ports.idempotency import build_intent_idempotency_key"

if old not in text:
    raise SystemExit("No se encontró el import erróneo esperado.")

path.write_text(text.replace(old, new))
print("[ok] import corregido en apps/external_actions/services.py")
