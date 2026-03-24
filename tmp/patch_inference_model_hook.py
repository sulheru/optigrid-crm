from pathlib import Path
import subprocess

path = Path("apps/inferences/models.py")

text = path.read_text()

# 1. añadir import
if "create_recommendation_from_inference" not in text:
    text = text.replace(
        "from django.db import models",
        "from django.db import models\nfrom apps.recommendations.services import create_recommendation_from_inference"
    )

# 2. añadir override save (solo si no existe)
if "def save(self, *args, **kwargs):" not in text:

    hook = """

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            try:
                create_recommendation_from_inference(self)
            except Exception:
                pass
"""

    # insertar al final de la clase
    text = text.replace(
        "\nclass Meta:",
        hook + "\n    class Meta:"
    )

path.write_text(text)
print("PATCHED inference model hook")


# 3. compile
subprocess.run([
    "python3", "-m", "py_compile",
    "apps/inferences/models.py"
], check=True)

# 4. tests
subprocess.run([
    "python3", "manage.py", "test", "apps.emailing.tests"
])
