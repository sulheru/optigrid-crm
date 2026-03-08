#!/usr/bin/env bash

set -e

echo "Corrigiendo AppConfig.name en apps Django..."

for dir in apps/*; do
    if [ -d "$dir" ]; then
        app=$(basename "$dir")
        file="$dir/apps.py"

        if [ -f "$file" ]; then
            echo "Actualizando $file"

            sed -i -E "s/name = '[^']+'/name = 'apps.${app}'/" "$file"
        fi
    fi
done

echo "Corrección completada."
