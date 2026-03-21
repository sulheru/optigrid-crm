import os
from pathlib import Path

def process_file(path):
    # Definimos las constantes aquí para evitar errores de Scope
    LLM_HINT_PY = "# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.\n"
    LLM_HINT_HTML = "{# LLM INFO: Ruta de origen de la plantilla. Django elimina este bloque al renderizar. #}\n"
    
    ext = path.suffix.lower()
    abs_path = str(path.resolve())
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 1. Limpieza de metadatos previos (evita duplicados y permite actualizar rutas)
        lines = [l for l in lines if not (
            l.startswith("# Ruta:") or 
            "LLM INFO:" in l or 
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
    extensions = {'.py', '.html'}
    ignored_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules'}

    print(f"--- Iniciando actualización de cabeceras en: {root_dir} ---")

    for path in root_dir.rglob('*'):
        # Ignorar directorios conflictivos
        if any(part in path.parts for part in ignored_dirs):
            continue
            
        if path.is_file() and path.suffix.lower() in extensions:
            # Evitar que el script se modifique a sí mismo
            if path.name == 'headers.py' or path.name == 'autoheaders.py':
                continue
            
            if process_file(path):
                count += 1
                print(f"[OK] {path.relative_to(root_dir)}")

    print(f"\n--- Proceso finalizado ---")
    print(f"Archivos modificados exitosamente: {count}")

if __name__ == "__main__":
    main()
