from pathlib import Path

path = Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/services_llm.py")
text = path.read_text()

if 'source="llm"' in text or "source='llm'" in text:
    print("services_llm.py already sets source")
    raise SystemExit(0)

patterns = [
    "AIRecommendation.objects.create(",
    "AIRecommendation(",
]

for pattern in patterns:
    start = 0
    changed = False
    while True:
        idx = text.find(pattern, start,
                source=AIRecommendation.SOURCE_LLM)
        if idx == -1:
            break
        end = text.find(")", idx)
        if end == -1:
            break
        block = text[idx:end]
        if "source=" not in block:
            text = text[:end] + ',\n            source="llm"' + text[end:]
            changed = True
            start = end + 1
        else:
            start = end + 1

    if changed:
        path.write_text(text)
        print("Patched services_llm.py")
        raise SystemExit(0)

raise SystemExit("Could not patch services_llm.py automatically")
