#!/usr/bin/env bash
set -euo pipefail

OUTPUT_FILE="${1:-llm_context_optigrid_crm.txt}"
ROOT_DIR="${2:-.}"
INCLUDE_MIGRATIONS="${INCLUDE_MIGRATIONS:-0}"
INCLUDE_TESTS="${INCLUDE_TESTS:-0}"
INCLUDE_SCRIPTS="${INCLUDE_SCRIPTS:-0}"
MAX_FILE_SIZE="${MAX_FILE_SIZE:-200000}"

cd "$ROOT_DIR"
ROOT_ABS="$(pwd)"

TMP_TREE="$(mktemp)"
TMP_FILES="$(mktemp)"

cleanup() {
  rm -f "$TMP_TREE" "$TMP_FILES"
}
trap cleanup EXIT

should_include_file() {
  local rel="$1"
  local base
  base="$(basename "$rel")"

  # Exclusiones duras
  case "$rel" in
    ./.git/*|./.venv/*|./venv/*|./__pycache__/*|*/__pycache__/*)
      return 1
      ;;
    ./db.sqlite3|*.pyc|*.pyo|*.sqlite3|*.log|*.bak)
      return 1
      ;;
    ./backups/*)
      return 1
      ;;
  esac

  # Excluir migraciones salvo que se pidan
  if [[ "$INCLUDE_MIGRATIONS" != "1" ]]; then
    case "$rel" in
      */migrations/*)
        return 1
        ;;
    esac
  fi

  # Excluir tests salvo que se pidan
  if [[ "$INCLUDE_TESTS" != "1" ]]; then
    case "$rel" in
      ./tests/*|*/tests.py)
        return 1
        ;;
    esac
  fi

  # Excluir scripts salvo que se pidan
  if [[ "$INCLUDE_SCRIPTS" != "1" ]]; then
    case "$rel" in
      ./scripts/*)
        return 1
        ;;
    esac
  fi

  # Incluir directorios principales del proyecto
  case "$rel" in
    ./apps/*|./config/*|./services/*|./templates/*|./requirements/*|./docs/*)
      return 0
      ;;
  esac

  # Incluir ficheros útiles en raíz
  case "$base" in
    manage.py|Dockerfile|docker-compose.yml|CHANGELOG.md|HANDOFF_CURRENT.md|NEXT_SESSION.md)
      return 0
      ;;
  esac

  # Incluir algunos scripts/parches raíz porque aquí sí pueden aportar contexto real
  case "$base" in
    fix_django_app_names.sh|parche*.py|patch*.py)
      return 0
      ;;
  esac

  return 1
}

is_text_file() {
  local f="$1"
  grep -Iq . "$f" 2>/dev/null
}

build_filtered_tree() {
  echo "."
  find . -type d \
    ! -path "./.git*" \
    ! -path "./.venv*" \
    ! -path "./venv*" \
    ! -path "*/__pycache__*" \
    ! -path "./backups*" \
    | sort
}

{
  echo "==== PROJECT ROOT ===="
  echo "$ROOT_ABS"
  echo
  echo "==== GENERATION SETTINGS ===="
  echo "OUTPUT_FILE=$OUTPUT_FILE"
  echo "INCLUDE_MIGRATIONS=$INCLUDE_MIGRATIONS"
  echo "INCLUDE_TESTS=$INCLUDE_TESTS"
  echo "INCLUDE_SCRIPTS=$INCLUDE_SCRIPTS"
  echo "MAX_FILE_SIZE=$MAX_FILE_SIZE"
  echo
} > "$OUTPUT_FILE"

{
  echo "==== FILTERED TREE ===="
  build_filtered_tree
  echo
} >> "$OUTPUT_FILE"

find . -type f | sort > "$TMP_FILES"

{
  echo "==== FILE CONTENTS ===="
  echo
} >> "$OUTPUT_FILE"

while IFS= read -r file; do
  if ! should_include_file "$file"; then
    continue
  fi

  if [[ ! -f "$file" ]]; then
    continue
  fi

  size="$(wc -c < "$file" | tr -d ' ')"
  if [[ "$size" -gt "$MAX_FILE_SIZE" ]]; then
    {
      echo "===== FILE: $(realpath "$file") ====="
      echo "[SKIPPED: file too large (${size} bytes)]"
      echo "===== EOF: $(realpath "$file") ====="
      echo
    } >> "$OUTPUT_FILE"
    continue
  fi

  if ! is_text_file "$file"; then
    {
      echo "===== FILE: $(realpath "$file") ====="
      echo "[SKIPPED: non-text or binary file]"
      echo "===== EOF: $(realpath "$file") ====="
      echo
    } >> "$OUTPUT_FILE"
    continue
  fi

  {
    echo "===== FILE: $(realpath "$file") ====="
    cat "$file"
    echo
    echo "===== EOF: $(realpath "$file") ====="
    echo
  } >> "$OUTPUT_FILE"

done < "$TMP_FILES"

echo "Context dump generado en: $(realpath "$OUTPUT_FILE")"
