# HANDOFF — OptiGrid CRM

## Estado actual

FASE: External Actions — Approval + Execution Pipeline COMPLETADA

El sistema dispone de:

- ExternalActionIntent estable
- Approval flow implementado
- Dispatcher limpio, no recursivo y determinista
- Execution desacoplada (email_stub)
- Idempotencia garantizada
- Persistencia de errores robusta (failure-safe)
- Tests 100% en verde

## Decisiones críticas fijadas

- ❌ No auto-dispatch
- ❌ No auto-send (implementado pero desactivado)
- ✅ Human-in-the-loop por defecto
- ✅ Ejecución siempre explícita
- ✅ Riesgo basado en irreversibilidad (no en canal)

## Arquitectura consolidada

Recommendation
→ ExternalActionIntent
→ (Approval)
→ Dispatch explícito
→ Execution (stub)
→ Persistencia consistente (success / failure)

## Siguiente foco

NO UI.
NO providers reales todavía.

Siguiente bloque prioritario:

👉 Knowledge + Behavior Ingestion Pipeline V1

- lectura de emails
- memoria vectorial
- detección de patrones
- generación de knowledge candidates

## Notas clave

- El sistema NO automatiza acciones externas
- Sí aprende desde el día cero
- La IA propone, no ejecuta

