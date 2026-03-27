from pathlib import Path

path = Path("apps/external_actions/tests.py")
text = path.read_text()

old = """        recommendation = AIRecommendation.objects.create(
            recommendation_type="followup",
            title="Follow up with contact",
            content="Prepare a polite follow-up.",
            rationale="No reply in thread.",
            confidence=0.75,
            status="new",
        )"""

new = """        recommendation = _make_recommendation(
            recommendation_type="followup",
            title="Follow up with contact",
            content="Prepare a polite follow-up.",
            rationale="No reply in thread.",
            confidence=0.75,
            status="new",
        )"""

count_before = text.count(old)
if count_before == 0:
    raise SystemExit("No se encontraron bloques AIRecommendation.objects.create(...) para sustituir.")

text = text.replace(old, new)
path.write_text(text)
print(f"[ok] reemplazados {count_before} bloques de creación rígida por _make_recommendation(...)")
