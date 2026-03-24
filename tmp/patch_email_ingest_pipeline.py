from pathlib import Path

path = Path("apps/services/email_ingest.py")
text = path.read_text()

# asegurar import real (eliminar fallback silencioso)
text = text.replace(
    "create_recommendation_from_inference = None",
    "from apps.recommendations.services import create_recommendation_from_inference"
)

# insertar hook tras creación de inferencias
if "create_recommendation_from_inference(inference)" not in text:
    text = text.replace(
        "inference = InferenceRecord.objects.create(",
        "inference = InferenceRecord.objects.create("
    )

    text = text.replace(
        ")\n",
        ")\n        try:\n            create_recommendation_from_inference(inference)\n        except Exception:\n            pass\n",
        1
    )

path.write_text(text)
print("patched email_ingest pipeline")


# compile
import subprocess
subprocess.run([
    "python3", "-m", "py_compile",
    "apps/services/email_ingest.py"
], check=True)

# run quick pipeline test if exists
subprocess.run([
    "python3", "manage.py", "test", "apps.emailing.tests"
])
