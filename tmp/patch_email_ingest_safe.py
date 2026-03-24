import subprocess
from pathlib import Path

# 1. localizar fichero real
result = subprocess.run(
    ["rg", "-l", "InferenceRecord", "apps"],
    capture_output=True,
    text=True
)

candidates = [p for p in result.stdout.splitlines() if "ingest" in p or "email" in p]

if not candidates:
    print("ERROR: no se encontró email_ingest")
    exit(1)

target = candidates[0]
print(f"USING FILE: {target}")

path = Path(target)
text = path.read_text()


# 2. asegurar import correcto
if "create_recommendation_from_inference" not in text:
    text = text.replace(
        "from apps.inferences.models import InferenceRecord",
        "from apps.inferences.models import InferenceRecord\nfrom apps.recommendations.services import create_recommendation_from_inference"
    )


# 3. insertar hook tras creación de inferencia
if "create_recommendation_from_inference(inference)" not in text:
    text = text.replace(
        "InferenceRecord.objects.create(",
        "InferenceRecord.objects.create("
    )

    # intento simple: añadir justo después del create
    text = text.replace(
        ")\n",
        ")\n        try:\n            create_recommendation_from_inference(inference)\n        except Exception:\n            pass\n",
        1
    )


path.write_text(text)
print("PATCHED:", target)


# 4. compile
subprocess.run(["python3", "-m", "py_compile", target], check=True)

# 5. test rápido
subprocess.run(["python3", "manage.py", "test", "apps.emailing.tests"])
