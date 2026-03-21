# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/autoheaders.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
import os
import sys
from pathlib import Path

# Configuración de metadatos para LLMs

def process_file(path):
    ext = path.suffix.lower()
    abs_path = str(path.resolve())
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 1. Limpieza de metadatos previos (evita duplicados)
        lines = [l for l in lines if not (
            l.startswith("# Ruta:") or 
            (l.startswith("{# Ruta:") and l.strip().endswith("#}"))
        )]

        if ext == '.py':
            header = [f"# Ruta: {abs_path}\n", LLM_HINT_PY]
            # Respetar el shebang (#! /usr/bin/env python)
            insert_pos = 1 if (lines and lines[0].startswith("#!")) else 0
            lines[insert_pos:insert_pos] = header
            
        elif ext == '.html':
            header = [f"{{# Ruta: {abs_path} #}}\n", LLM_HINT_HTML]
            lines = header + lines

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"Error procesando {path}: {e}")
        return False

def main():
    root_dir = Path.cwd()
    count = 0
    # Extensiones a procesar
    extensions = {'.py', '.html'}
    # Carpetas a ignorar para evitar tocar librerías o git
    ignored_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules'}

    print(f"--- Iniciando actualización de cabeceras en: {root_dir} ---")

    for path in root_dir.rglob('*'):
        # Filtrar por carpetas ignoradas
        if any(part in path.parts for part in ignored_dirs):
            continue
            
        if path.is_file() and path.suffix.lower() in extensions:
            # No procesar este propio script
            if path.name == 'headers.py':
                continue
            
            if process_file(path):
                count += 1
                print(f"[OK] {path.relative_to(root_dir)}")

    print(f"--- Proceso finalizado. Archivos modificados: {count} ---")

if __name__ == "__main__":
    main()
