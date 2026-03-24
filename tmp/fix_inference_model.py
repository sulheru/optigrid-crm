from pathlib import Path
import subprocess
import re

path = Path("apps/inferences/models.py")
text = path.read_text()

# 1. eliminar import problemático
text = text.replace(
    "from apps.recommendations.services import create_recommendation_from_inference\n",
    ""
)

# 2. eliminar override save completo
text = re.sub(
    r"\n\s*def save\(self, \*args, \*\*kwargs\):.*?pass\n",
    "\n",
    text,
    flags=re.DOTALL
)

path.write_text(text)
print("CLEANED inference model")


# 3. compile
subprocess.run([
    "python3", "-m", "py_compile",
    "apps/inferences/models.py",
    "apps/recommendations/services.py"
], check=True)

# 4. test
subprocess.run([
    "python3", "manage.py", "test", "apps.emailing.tests"
])
