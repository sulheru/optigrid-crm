# OptiGrid CRM — NEXT SESSION

## Objetivo principal

Completar la capa operativa del CRM.

La Recommendation Operations Layer ya está implementada.

El siguiente paso es mejorar:

Tasks  
Opportunities

## Prioridad 1 — Mejorar Tasks

Añadir mejoras a:

/tasks/

Mejoras previstas:

- filtros por status
- filtros por task_type
- indicador visual de prioridad
- indicador visual de estado
- enlace directo a recommendation origen

Opcional:

- mostrar due_at
- ordenar por prioridad

## Prioridad 2 — Mejorar Opportunities

La vista actual es muy básica.

Añadir:

stage  
confidence  
summary  
estimated_value

Esto permitirá convertir opportunities en entidades comerciales reales.

## Prioridad 3 — Promotion desde Recommendations

Añadir botón:

Promote to Opportunity

Esto permitiría:

AIRecommendation → Opportunity

sin necesidad de pasar por Task.

Debe incluir reglas de seguridad para evitar generar oportunidades falsas.

## Prioridad 4 — Observabilidad

Ampliar:

crm_pipeline_report

para incluir:

- opportunities por stage
- recommendations por confidence
- tasks por priority

## Objetivo estratégico

Completar el primer CRM IA-first completamente operativo basado en señales
de conversación.

