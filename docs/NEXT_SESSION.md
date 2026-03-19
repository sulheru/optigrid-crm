# NEXT SESSION — OptiGrid CRM

---

## CONTEXTO

Sistema evolucionando hacia:

AI Commercial Operating System

Base ya implementada:

- CRM Core
- Opportunity Intelligence
- Governance base
- Strategy Chat V1

---

## OBJETIVO DE LA SESIÓN

Iniciar FASE 4:

TARGET INTELLIGENCE LAYER

---

## BLOQUE 1 — MODELOS

Crear:

- LeadSuggestion
- LeadSignal
- LeadResearchSnapshot

Ubicación:
apps/lead_research/models.py

---

## BLOQUE 2 — SCHEMAS

Crear:

- lead discovery schema
- enrichment schema
- hypothesis schema

Ubicación:
apps/lead_research/schemas.py

---

## BLOQUE 3 — DISCOVERY ENGINE

Crear servicio:

apps/lead_research/services/signal_discovery.py

Responsable de:

- generar queries dinámicas
- llamar a Gemini
- validar output
- deduplicar
- persistir sugerencias

---

## BLOQUE 4 — MEMORY

Evitar repetición de:

- companies existentes
- suggestions previas
- dismissed

---

## BLOQUE 5 — BACKGROUND TASK

Celery task:

- ejecutar discovery periódicamente

---

## BLOQUE 6 — UI

Vista mínima:

- lista de sugerencias
- acciones:
  - approve
  - dismiss
  - reopen

---

## REGLAS

- todo estructurado (no texto libre)
- usar Pydantic
- logs claros
- no romper pipeline actual

---

## RESULTADO ESPERADO

Sistema capaz de:

- descubrir nuevas empresas automáticamente
- evitar duplicados
- generar contexto útil
- preparar base para pipeline automático

---

## NOTA

Esto es el punto de entrada del sistema autónomo completo.

