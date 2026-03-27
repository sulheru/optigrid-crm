from pathlib import Path

path = Path("apps/external_actions/tests.py")
text = path.read_text()

old = """    payload.update(overrides)
    return AIRecommendation.objects.create(**payload)
"""

new = """    safe_overrides = {k: v for k, v in overrides.items() if k in field_names}
    payload.update(safe_overrides)
    return AIRecommendation.objects.create(**payload)
"""

if old not in text:
    raise SystemExit("No se encontró el bloque payload.update(overrides) esperado.")

path.write_text(text.replace(old, new))
print("[ok] _make_recommendation ahora filtra overrides por campos reales del modelo")
