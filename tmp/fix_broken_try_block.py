from pathlib import Path
import re

path = Path("apps/external_actions/services/core.py")
text = path.read_text()

# 1. Eliminar try/except vacíos completos
text = re.sub(
    r"\n\s*try:\s*\n\s*except Exception:\s*\n\s*pass",
    "\n",
    text,
    flags=re.MULTILINE
)

# 2. Eliminar cualquier try: sin contenido (caso más general)
text = re.sub(
    r"\n\s*try:\s*\n\s*except Exception:\s*",
    "\n",
    text,
    flags=re.MULTILINE
)

# 3. Limpieza adicional: bloques try con solo comentarios o espacios
text = re.sub(
    r"\n\s*try:\s*\n(\s*#.*\n)*\s*except Exception:\s*\n(\s*#.*\n)*",
    "\n",
    text,
    flags=re.MULTILINE
)

path.write_text(text)
print("[ok] broken try/except blocks removed")
