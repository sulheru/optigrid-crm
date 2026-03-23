# HANDOFF CURRENT

## Proyecto
OptiGrid CRM — AI Commercial Operating System

## Fecha
2026-03-23

## Estado de la sesión
Sesión de auditoría global y rediseño del roadmap.

No se ha implementado código nuevo.
No se ha refactorizado nada.
La sesión se ha dedicado a inspección real y decisiones de arquitectura.

---

## Hallazgos principales

### 1. Estado real del sistema
El sistema ya tiene backend significativo y no está en fase meramente conceptual.

Se han confirmado piezas reales:

- `AIRecommendation` como entidad operativa
- execution layer en recommendations
- task materialization
- opportunity promotion
- pipeline `services/` con:
  - email_ingest
  - fact_extraction
  - inference_engine
  - update_proposals
- inbox intelligence paralela en `apps/emailing`
- strategy backend con selección rule-based / Gemini parcial
- dashboard / recommendations / tasks / inbox / opportunities con base UI V2 parcial

### 2. Problema estructural real
No existe todavía una capa backend plenamente unificada.

Conviven al menos dos lógicas/pipelines relevantes:

- pipeline facts → inferences → proposals → recommendations
- pipeline inbox interpretation → decision → apply

Además:
- la simulación de correo sigue embebida en el flujo operativo
- no existe todavía provider abstraction layer formal
- no existe todavía SOI implementado
- Outlook y Calendar reales no están conectados

### 3. Conclusión estratégica
La prioridad correcta ya no es UI ni plugins directos.

La prioridad correcta es:

**consolidar el backend canónico antes de enchufar integraciones externas**

---

## Decisión tomada
Se redefine el roadmap del proyecto en clave backend-first:

1. CONTROL Y CANONICAL BACKEND
2. PROVIDER ABSTRACTION LAYER
3. SCENARIO ORCHESTRATOR INTERFACE (SOI)
4. REAL INTEGRATIONS
5. EXECUTIVE SURFACES

---

## Notas importantes
- El SOI fue introducido como idea tardía en esta sesión y queda aceptado como futura capa de orquestación.
- Calendar se considera útil no solo como agenda, sino como canal de recordatorios y notificaciones móviles.
- Tasks debe seguir siendo fuente de verdad operativa; Calendar será proyección/sincronización cuando convenga.

---

## Qué NO hacer en la siguiente sesión
- no empezar aún por Outlook real
- no empezar aún por Calendar real
- no implementar aún SOI completo
- no saltar directamente a plugins sin cerrar backend

---

## Qué SÍ hacer en la siguiente sesión
- comenzar FASE A: CONTROL Y CANONICAL BACKEND
- diseñar estructura backend objetivo
- decidir pipeline canónico
- identificar puntos de mezcla entre:
  - core
  - providers
  - simulación
  - views
- preparar la futura provider abstraction layer

