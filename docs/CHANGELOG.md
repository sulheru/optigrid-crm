# CHANGELOG.md

## 2026-03-18 — OPPORTUNITY INTELLIGENCE V2
Se refactorizó el análisis de oportunidades abiertas para evolucionar de comando manual a servicio reutilizable.

Cambios:
- `last_analyzed_at` en `Opportunity`
- `should_analyze()` para evitar reanálisis innecesario
- scoring interpretable
- `risk_flags`
- `next_actions`
- mantenimiento de dedupe/reuse de recomendaciones

Impacto:
- Opportunity Intelligence pasa a ser una capa analítica real, no solo un comando batch.

---

## 2026-03-18 — AUTOMATION PREP
Se preparó la automatización periódica vía Celery para análisis de oportunidades.

Cambios:
- task periódica para analizar oportunidades abiertas
- settings configurables para frecuencia, batch y recheck window
- integración con el core existente de análisis

Impacto:
- el sistema queda preparado para pasar de análisis manual a análisis continuo.

---

## 2026-03-18 — PRIORITIZED OPPORTUNITIES UI
Se implementó una vista de priorización de oportunidades.

Cambios:
- ruta `/opportunities/prioritized/`
- score, priority bucket, risk flags y next actions en UI
- execution status
- filtros por stage y needs attention
- KPIs de resumen

Impacto:
- aparece un panel operativo de lectura para supervisión comercial.

---

## 2026-03-18 — AUTOTASKING V1
Se añadió materialización automática de tasks a partir de `next_actions`, controlada por feature flag.

Cambios:
- `AUTO_TASKING_ENABLED`
- `AUTO_TASKING_MIN_PRIORITY`
- `AUTO_TASKING_ALLOWED_ACTIONS`
- servicio `autotasker.py`
- dedupe de autotasks
- integración con `analyze_opportunity()`

Impacto:
- el sistema no solo propone acciones, también puede empezar a ejecutarlas.

---

## 2026-03-18 — TASK TRACEABILITY
Se enriqueció `CRMTask` para soportar trazabilidad de automatización.

Cambios:
- FK `opportunity`
- campo `source`
- campo `source_action`

Impacto:
- se distingue tarea manual de automática.
- mejora de trazabilidad y de lectura operativa.

---

## 2026-03-18 — OPPORTUNITY TASK DETAIL VIEW
Se implementó vista dedicada de tasks por oportunidad.

Cambios:
- ruta `/opportunities/<id>/tasks/`
- detalle de tasks por oportunidad
- visualización de `source_action`, estado, vencimiento y tipo
- enlace desde la vista priorizada

Impacto:
- la UI ya permite inspección operativa real por oportunidad.
