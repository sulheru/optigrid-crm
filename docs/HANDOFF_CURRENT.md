# HANDOFF_CURRENT.md

## Proyecto
OptiGrid CRM — IA-First CRM System

## Fecha de cierre
2026-03-18

## Estado actual
El sistema ha evolucionado desde un pipeline CRM funcional a una capa operativa de inteligencia sobre oportunidades.

Pipeline estable:
Email → Fact → Inference → Proposal → Recommendation → Task → Opportunity

Capas activas al cierre:
- Opportunity Intelligence V2
- Prioritized Opportunities UI
- Autotasking V1 con feature flag

## Lo completado en esta sesión

### 1. Opportunity Intelligence V2
Se refactorizó el análisis de oportunidades abiertas para pasar de un comando manual simple a un análisis reutilizable y preparado para automatización.

Implementado:
- `last_analyzed_at` en `Opportunity`
- lógica `should_analyze()` para evitar reanálisis innecesario
- scoring interpretable por oportunidad
- generación de `risk_flags`
- generación de `next_actions`
- salida estructurada preparada para priorización futura
- mantenimiento del dedupe/reuse de recomendaciones

### 2. Automatización preparada con Celery
Se dejó preparada la automatización periódica para analizar oportunidades abiertas.

Implementado:
- task periódica de Celery para análisis de oportunidades
- settings configurables para frecuencia, batch size y recheck window
- el comando manual sigue existiendo y reutiliza el core

Nota:
No se validó en esta sesión el worker/beat en ejecución real, pero la integración de código quedó preparada.

### 3. Prioritized Opportunities UI + backend
Se construyó una vista analítica de oportunidades priorizadas.

Ruta:
- `/opportunities/prioritized/`

Capacidades:
- orden por relevancia
- score por oportunidad
- priority bucket
- risk flags
- next actions
- execution status
- filtro por stage
- filtro `needs attention`
- KPIs superiores

La UI fue diseñada deliberadamente como read model analítico para no tener que rehacerla cuando el sistema materializa tasks de forma automática.

### 4. Autotasking V1
Se añadió una capa operativa para crear tasks automáticamente a partir de `next_actions`, controlada por feature flag.

Implementado:
- `AUTO_TASKING_ENABLED`
- `AUTO_TASKING_MIN_PRIORITY`
- `AUTO_TASKING_ALLOWED_ACTIONS`
- nuevo servicio `autotasker.py`
- mapping acción → task_type
- dedupe de autotasks
- integración dentro de `analyze_opportunity()`

Comportamiento validado:
- con autotasking apagado: analiza y prioriza, pero no crea tasks
- con autotasking encendido: crea tasks auto para oportunidades por encima del umbral
- oportunidades en `monitor` no materializan tasks si el mínimo es `medium`

### 5. Trazabilidad de tareas automáticas
Se enriqueció `CRMTask` para distinguir tareas manuales de automáticas.

Añadido en `CRMTask`:
- FK `opportunity`
- `source` = manual/auto
- `source_action`

### 6. Vista de tasks por oportunidad
Se construyó una vista dedicada para inspeccionar tasks por oportunidad.

Ruta:
- `/opportunities/<id>/tasks/`

Capacidades:
- ver todas las tasks de la oportunidad
- distinguir auto vs manual
- mostrar `source_action`
- mostrar prioridad, estado y vencimiento
- enlazada desde la vista priorizada

## Validación realizada

### Comando manual
Se validó:
- `python manage.py check`
- `python manage.py analyze_open_opportunities --force`

Resultados observados:
- Opportunity 1: score alto, priority high, autotasks creadas correctamente
- Opportunity 4: score alto, priority high, autotask creada correctamente
- Opportunity 5: priority monitor, sin autotask por quedar debajo del umbral

### UI validada
Se comprobó visualmente:
- `/opportunities/prioritized/`
- `/opportunities/1/tasks/`

Resultado:
- la vista priorizada muestra `auto_task_open` cuando corresponde
- muestra contador de autotasks
- muestra mini resumen de tasks auto
- la vista de detalle muestra tasks auto con `source_action`

## Estado funcional al cierre
El sistema ya no es solo un CRM con pipeline interno, sino un sistema comercial semiautónomo con ciclo:

Opportunity Intelligence
↓
Scoring + risks + next actions
↓
Autotasking controlado por flag
↓
CRMTask auto creada con trazabilidad
↓
UI operativa de lectura y supervisión

## Restricciones / puntos a vigilar
1. El mapping semántico entre `next_actions` y `task_type` funciona, pero conviene pulirlo en la siguiente sesión para que nombres y ejecución hablen el mismo idioma.
2. Los labels en UI aún muestran algunos slugs técnicos (`auto_task_open`, `define_next_action`, etc.).
3. Celery quedó preparado, pero falta validar worker + beat en ejecución real si se quiere dar por cerrada la automatización completa.
4. El flujo de autotasking está bien para V1, pero aún no incluye acciones de revocación, confirmación humana opcional o gobernanza adicional.

## Ficheros principales tocados en esta sesión
- `apps/opportunities/models.py`
- `apps/opportunities/services/opportunity_analyzer.py`
- `apps/opportunities/services/prioritization.py`
- `apps/opportunities/services/autotasker.py`
- `apps/opportunities/tasks.py`
- `apps/opportunities/views_prioritized.py`
- `apps/opportunities/urls.py`
- `apps/opportunities/management/commands/analyze_open_opportunities.py`
- `apps/tasks/models.py`
- `config/celery.py`
- `config/settings.py`
- `config/urls.py`
- `templates/opportunities/prioritized.html`
- `templates/opportunities/opportunity_tasks.html`
- migraciones de `opportunities` y `tasks`

## Recomendación principal para la siguiente sesión
No ampliar más superficie nueva todavía.

La siguiente sesión debería centrarse en:
1. pulido semántico y UX de la capa creada
2. validación real de Celery beat/worker
3. cierre operativo con commit limpio, revisión de migraciones y documentación
