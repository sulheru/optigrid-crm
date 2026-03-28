#!/bin/bash

echo "Limpiando sesión"
rm -rf tmp/*

echo "Creando huella de arbol de ficheros"
tree > docs/CURRENT_TREE.txt

echo "Generando Commit"

git add .

# Validación mensaje
if [ -z "$1" ]; then
  echo "❌ Debes proporcionar un mensaje de commit"
  echo "Uso: ./cleansession.sh \"mensaje del commit\""
  exit 1
fi

# Evitar commit vacío
if git diff --cached --quiet; then
  echo "⚠️ No hay cambios para commitear"
  exit 0
fi

# Commit con timestamp
git commit -m "$(date '+%Y-%m-%d %H:%M') — $1"

echo "Finalizado"
