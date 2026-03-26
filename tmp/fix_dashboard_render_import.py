from pathlib import Path

path = Path("apps/dashboard_views.py")
text = path.read_text(encoding="utf-8")

if "from django.shortcuts import render" not in text:
    lines = text.splitlines()

    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_idx = i + 1

    lines.insert(insert_idx, "from django.shortcuts import render")
    text = "\n".join(lines)

    path.write_text(text, encoding="utf-8")
    print("[ok] render import added")
else:
    print("[ok] render already present")
