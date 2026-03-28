#!/bin/bash

echo "Limpiando sesión"
rm -rf tmp/*

echo "Creando huella de arbol de ficheros"
tree > docs/CURRENT_TREE.md

echo "Generando Commit"

git add .

# Validación básica
if [ -z "$1" ]; then
  echo "❌ Debes proporcionar un mensaje de commit"
  echo "Uso: ./cleansession.sh \"mensaje del commit\""
  exit 1
fi

git commit -m "$1"

echo "Finalizado"
