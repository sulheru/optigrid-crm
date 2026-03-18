# NEXT SESSION — Opportunity Intelligence V2

## Objetivo

Convertir Opportunity Intelligence en un sistema autónomo.

---

## Prioridad 1 — Automatización

Implementar ejecución automática:

### Opción A (simple)
- Django management command vía cron

### Opción B (recomendada)
- Celery periodic task
- Intervalo configurable (ej: cada 15 min)

---

## Prioridad 2 — Tracking

Añadir campo a Opportunity:

- last_analyzed_at

Evitar análisis redundante innecesario.

---

## Prioridad 3 — Inteligencia

Mejorar lógica de análisis:

- usar más señales del contexto:
  - inference_type
  - fact_type
  - timing
  - engagement
- scoring de oportunidad
- detección de "stalled opportunities"

---

## Prioridad 4 — Priorización

Crear:

Daily Prioritization Layer

Salida:

- Top oportunidades a trabajar hoy
- Alertas
- Acciones sugeridas

---

## Objetivo final

Pasar de:

"comando manual de análisis"

a:

"sistema que monitoriza y actúa automáticamente"

---

## Regla clave

Mantener:

- trazabilidad
- no duplicación
- separación hecho / inferencia / decisión
