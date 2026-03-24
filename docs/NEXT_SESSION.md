# NEXT SESSION

## CONTEXTO

Merge Layer V1 completada
Sistema coherente y sin duplicados

---

## OBJETIVO

COCKPIT V3 — NEXT BEST ACTION ENGINE

---

## IMPLEMENTACIÓN

### 1. NBA Engine

Input:
- recommendations (merged, status=new)

Compute:
- urgency_score (rules)
- type_weight (hardcoded)
- final score

score = confidence + urgency + type_weight

Output:
- 1 recommendation (top)

---

### 2. Urgency Rules

Ejemplo:

- email reciente → alta urgencia
- sin respuesta → media
- frío → baja

---

### 3. Type Weights

Ejemplo:

- followup → 1.0
- contact_strategy → 0.6
- review → 0.3

---

### 4. Dashboard

Nuevo bloque:

"What should you do now"

---

## REGLAS

- no persistir scoring
- no romper execution
- no duplicar lógica
- validar antes de implementar

---

## CRITERIO DE ÉXITO

- 1 acción clara
- ranking consistente
- comportamiento determinista

