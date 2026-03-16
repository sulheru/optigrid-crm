# OptiGrid CRM — CHANGELOG

## 2026-03-09

### Recommendation Operations Layer

Se implementa la primera capa operativa del CRM IA-first.

Las recomendaciones generadas por el motor de inferencias ahora pueden
convertirse en acciones reales desde la interfaz.

### Cambios principales

#### UI

Nueva operativa en:

/recommendations/

Acciones disponibles:

- Create Task
- Dismiss Recommendation

Las acciones modifican el estado de `AIRecommendation`.

Estados operativos:

- new
- materialized
- dismissed
- executed

#### Tasks UI

La vista `/tasks/` ahora permite cambiar el estado de las tareas.

Acciones:

- Start → in_progress
- Done → done
- Dismiss → dismissed
- Reopen → open

Esto convierte la lista de tareas en un panel operativo.

#### Mapping Recommendation → Task

Se añade un mapeo explícito entre:

AIRecommendation.recommendation_type  
CRMTask.task_type

Esto evita inconsistencias entre el motor de recomendaciones y el modelo
de tareas.

Ejemplos:

reply_strategy → reply_email  
followup → follow_up  
qualification → review_manually  
pricing_strategy → review_manually

#### CLI

Nuevo comando:

python manage.py crm_pipeline_report

Permite validar rápidamente el estado del pipeline.

Incluye:

- emails
- facts
- inferences
- proposals
- recommendations
- tasks
- opportunities

También muestra estadísticas por tipo y estado.

### Estado actual del pipeline

emails=48  
facts=45  
inferences=66  
proposals=21  
recommendations=34  
tasks=34  
opportunities=3

La arquitectura IA-first está completamente operativa.


## 2026-03-16

### Added
Opportunity Intelligence Layer V1

New command:

    python manage.py analyze_opportunity <id>

Features:

- reconstructs full context chain
- derives reasoning from email → fact → inference
- generates opportunity-level recommendations
- prevents duplicate recommendations
- reuses existing ones when applicable

Context builder enhancements:

- alias normalization for scope_type
- reverse lineage reconstruction
- inference → fact → email tracing
- contextual summary generation

### Result
CRM opportunities can now be analyzed with full pipeline awareness.
