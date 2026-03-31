#!/bin/bash

echo "🧹 Limpiando sesión..."

# 1. Limpiar temporales
rm -rf tmp/*
mkdir -p tmp

# 2. Limpiar __pycache__ (ruido típico)
find . -type d -name "__pycache__" -exec rm -rf {} +

# 3. Snapshot del árbol del proyecto
echo "🌳 Generando árbol de ficheros..."
tree -I ".git|__pycache__|tmp|.venv" > docs/CURRENT_TREE.md

# 4. Estado de git
echo "📊 Guardando estado git..."
git status > docs/GIT_STATUS.md

# 5. (Opcional) freeze de dependencias
if [ -f ".venv/bin/activate" ]; then
    echo "📦 Guardando dependencias..."
    source .venv/bin/activate
    pip freeze > docs/REQUIREMENTS_SNAPSHOT.txt
fi

# 6. Commit con mensaje dinámico
if [ -z "$1" ]; then
    echo "❌ Debes pasar un mensaje de commit"
    echo "Uso: ./cleansession.sh \"mensaje\""
    exit 1
fi

echo "📝 Creando commit..."
git add .
git commit -m "$1"

echo "✅ Sesión cerrada correctamente"
