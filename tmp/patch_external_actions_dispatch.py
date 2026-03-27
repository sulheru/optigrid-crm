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
