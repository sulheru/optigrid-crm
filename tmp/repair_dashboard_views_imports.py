from pathlib import Path

path = Path("apps/dashboard_views.py")
text = path.read_text(encoding="utf-8")

# elimina inserciones previas problemáticas
text = text.replace("from django.shortcuts import render\n", "")
text = text.replace("\nfrom django.shortcuts import render", "\n")

lines = text.splitlines()

# detectar el punto correcto: después del bloque inicial de imports
insert_at = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("from ") or stripped.startswith("import ") or stripped == "":
        insert_at = i + 1
        continue
    break

lines.insert(insert_at, "from django.shortcuts import render")

fixed = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
path.write_text(fixed, encoding="utf-8")

print("[ok] dashboard_views.py imports repaired")
