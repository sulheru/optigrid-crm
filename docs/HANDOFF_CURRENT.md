# HANDOFF — CURRENT STATE

## PROYECTO
OptiGrid CRM — AI Commercial Operating System

## FASE ACTUAL
RECOMMENDATION MERGE LAYER V1 — COMPLETADA

PRÓXIMA FASE:
COCKPIT V3 — NEXT BEST ACTION ENGINE

---

## ESTADO DEL SISTEMA

Pipeline operativo:

Email → Fact → Inference → (Rules + LLM) → Merge → Recommendations → Execution

---

## DECISIONES RECIENTES (CRÍTICAS)

### Merge Layer
- source: rules / llm / merged
- deduplicación por scope + type
- prioridad rules
- LLM solo enriquece

---

## NUEVA CAPA (EN DISEÑO)

### Next Best Action Engine (NBA)

Definición:
- el sistema selecciona UNA única acción global prioritaria

---

## DECISIONES ARQUITECTÓNICAS NBA

### Unidad de ranking
- Recommendations (no tasks, no opportunities)

### Tipo de ranking
- runtime (no persistido)

### Número de acciones
- UNA única NBA global

### Fórmula base

score = confidence + urgency + type_weight

---

### Urgency
- basada en reglas (no LLM)
- derivada de:
  - recencia
  - falta de respuesta
  - señales temporales

---

### Type Weight (hardcoded V1)

Ejemplo:

- followup → alto
- contact_strategy → medio
- review → bajo

---

### Explainability
- NO en V1

---

## HARD RULE GLOBAL

NINGUNA IA envía emails automáticamente

---

## RESULTADO

Sistema preparado para:

→ decisión global
→ cockpit operativo
→ ejecución guiada

