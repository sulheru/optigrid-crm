import subprocess
from pathlib import Path
import re

# buscar usos de create directo
result = subprocess.run(
    ["rg", "-l", "InferenceRecord.objects.create", "apps"],
    capture_output=True,
    text=True
)

files = [Path(p) for p in result.stdout.splitlines()]

print("FILES:", files)

for path in files:
    text = path.read_text()

    if "inferences.services" not in text:
        text = text.replace(
            "from apps.inferences.models import InferenceRecord",
            "from apps.inferences.models import InferenceRecord\nfrom apps.inferences.services import create_inference"
        )

    # reemplazo simple (seguro solo primera ocurrencia)
    text = text.replace(
        "InferenceRecord.objects.create(",
        "create_inference("
    )

    path.write_text(text)
    print("PATCHED:", path)


# compile
subprocess.run([
    "python3", "-m", "py_compile",
    *[str(p) for p in files],
    "apps/inferences/services.py"
], check=True)

# tests
subprocess.run([
    "python3", "manage.py", "test", "apps.emailing.tests"
])
