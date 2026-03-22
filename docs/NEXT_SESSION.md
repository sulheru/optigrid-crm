# NEXT SESSION

## Objetivo
Cerrar la capa visual y semántica de la UI empezando por Recommendations.

## Prioridad 1 — Recommendations UI
Inspeccionar y refactorizar:
- `templates/recommendations/list.html`

Objetivos:
- alinear con `base.html`
- usar el design system V2
- eliminar labels internas visibles
- usar `label_filters`

## Prioridad 2 — Semántica visual
Definir si conviene introducir:
- icono por `recommendation_type`
- color por prioridad
- color por estado

## Prioridad 3 — Cleanup
Buscar y eliminar:
- `|title` sobre campos semánticos
- strings internas expuestas en UI
- restos de layout legacy

## Restricción operativa
No asumir contexto.
Verificar primero el fichero real antes de modificar.
Entregar siempre ficheros completos con `cat > ...`.
