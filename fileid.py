# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/fileid.py
import os
from pathlib import Path

def prepend_filepath():
    # Obtenemos el directorio actual donde se ejecuta el script
    root_dir = Path.cwd()
    
    # Buscamos todos los archivos .py de forma recursiva
    for path in root_dir.rglob('*.py'):
        # Evitamos que el propio script se modifique a sí mismo
        if path.name == 'add_header.py':
            continue
            
        absolute_path = str(path.resolve())
        header = f"# Ruta: {absolute_path}\n"
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificamos si la ruta ya está escrita para no duplicar
            if not content.startswith("# Ruta:"):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(header + content)
                print(f"Actualizado: {path.name}")
            else:
                print(f"Omitido (ya tiene cabecera): {path.name}")
                
        except Exception as e:
            print(f"Error procesando {path}: {e}")

if __name__ == "__main__":
    prepend_filepath()
