import subprocess
from pathlib import Path
import re

# =========================
# 1. REVERTIR FICHERO ROTO
# =========================

bad_file = Path("apps/emailing/management/commands/crm_pipeline_report.py")

if bad_file.exists():
    print("Fixing broken file:", bad_file)

    text = bad_file.read_text()

    # eliminar líneas inyectadas incorrectamente
    text = re.sub(
        r"\n\s*try:\n\s*create_recommendation_from_inference\(inference\)\n\s*except Exception:\n\s*pass\n",
        "\n",
        text
    )

    # eliminar import si se añadió
    text = text.replace(
        "from apps.recommendations.services import create_recommendation_from_inference\n",
        ""
    )

    bad_file.write_text(text)


# =========================
# 2. LOCALIZAR INGEST REAL
# =========================

result = subprocess.run(
    ["rg", "-l", "InferenceRecord.objects.create", "apps"],
    capture_output=True,
    text=True
)

candidates = [
    p for p in result.stdout.splitlines()
    if "management/commands" not in p
]

if not candidates:
    print("ERROR: no ingest file found")
    exit(1)

target = candidates[0]
print("USING FILE:", target)

path = Path(target)
text = path.read_text()


# =========================
# 3. IMPORT CORRECTO
# =========================

if "create_recommendation_from_inference" not in text:
    text = text.replace(
        "from apps.inferences.models import InferenceRecord",
        "from apps.inferences.models import InferenceRecord\nfrom apps.recommendations.services import create_recommendation_from_inference"
    )


# =========================
# 4. INSERT SEGURO (NO GLOBAL)
# =========================

pattern = r"(inference\s*=\s*InferenceRecord\.objects\.create\([^\)]*\))"

def inject(match):
    block = match.group(1)
    return block + "\n        try:\n            create_recommendation_from_inference(inference)\n        except Exception:\n            pass"

if "create_recommendation_from_inference(inference)" not in text:
    text = re.sub(pattern, inject, text, count=1, flags=re.DOTALL)


path.write_text(text)
print("PATCHED:", target)


# =========================
# 5. VALIDACIÓN
# =========================

subprocess.run([
    "python3", "-m", "py_compile",
    str(bad_file),
    target
], check=True)

subprocess.run([
    "python3", "manage.py", "test", "apps.emailing.tests"
])
