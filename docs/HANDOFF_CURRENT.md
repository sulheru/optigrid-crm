# HANDOFF — CURRENT STATE

## Estado general

El sistema ha completado la estabilización del CORE CONTROL LAYER.

El flujo principal es ahora:

Recommendation → Execution → ExternalActionIntent → (Approval → Dispatch)

## Componentes clave

### Recommendations
- Creación centralizada en:
  apps/recommendations/services/factory.py
- Eliminadas rutas paralelas en producción

### Execution Layer
- Punto único:
  execute_recommendation_service
- Acciones soportadas:
  - reply_strategy → draft + external intent
  - followup → task
  - contact_strategy → task
  - opportunity_review → task (+ posible promoción)
  - advance_opportunity → stage++
  - mark_lost → stage=lost

### Inbound Pipeline
- Restaurado correctamente
- scope_type = inbound_email
- Mapping action → recommendation consistente

### External Actions
- Flujo completo:
  - create intent
  - approve
  - dispatch
- email.send sigue bloqueado (guardrail activo)

## Estado de tests

- Core tests: OK
- Emailing tests: OK
- External actions: OK
- Único fallo:
  apps.knowledge.tests (ImportError)

## Riesgos conocidos

- Módulo knowledge desalineado (no bloqueante)
- Observabilidad limitada (logs básicos)

## Conclusión

Sistema estable y preparado para integración de:
- Mail real (controlado)
- LLM
