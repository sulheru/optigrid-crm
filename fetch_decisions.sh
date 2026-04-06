#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:8000"

mkdir -p tmp

echo "== Generando 5 IDs aleatorios =="
IDS=$(shuf -i 1-28 -n 5)

echo "IDs seleccionados: $IDS"
echo ""

for ID in $IDS; do
  echo "== Decision $ID =="

  curl -s "$BASE_URL/inbox/$ID/decision/" > "tmp/decision_$ID.html"
  echo "  -> tmp/decision_$ID.html"

  echo ""
done

echo "Listado final:"
ls -lh tmp/decision_*.html 2>/dev/null || true
