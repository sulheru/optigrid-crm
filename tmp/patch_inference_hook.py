import subprocess
from pathlib import Path
import re

# 1. localizar TODOS los puntos donde se crean inferencias
result = subprocess.run(
    ["rg", "-l", "InferenceRecord.objects.create", "apps"],
    capture_output=True,
    text=True
)

files = [
    Path(p) for p in result.stdout.splitlines()
    if "management/commands" not in p
]

if not files:
    print("ERROR: no inference creation points found")
    exit(1)

print("FILES:", files)


for path in files:
    text = path.read_text()

    # asegurar import
    if "create_recommendation_from_inference" not in text:
        text = text.replace(
            "from apps.inferences.models import InferenceRecord",
            "from apps.inferences.models import InferenceRecord\nfrom apps.recommendations.services import create_recommendation_from_inference"
        )

    # insertar hook solo si no existe
    if "create_recommendation_from_inference(inference)" not in text:

        pattern = r"(inference\s*=\s*InferenceRecord\.objects\.create\([^\)]*\))"

        def inject(match):
            block = match.group(1)
            return block + "\n        try:\n            create_recommendation_from_inference(inference)\n        except Exception:\n            pass"

        new_text, count = re.subn(pattern, inject, text, count=1, flags=re.DOTALL)

        if count > 0:
            path.write_text(new_text)
            print("PATCHED:", path)
        else:
            print("SKIPPED (no match):", path)


# 2. compile todo lo tocado
subprocess.run([
    "python3", "-m", "py_compile",
    *[str(p) for p in files]
], check=True)

# 3. tests rápidos
subprocess.run([
    "python3", "manage.py", "test", "apps.emailing.tests"
])
