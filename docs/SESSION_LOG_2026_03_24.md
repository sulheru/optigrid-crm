# SESSION LOG — 2026-03-24

## FASE
Recommendation Merge Layer V1 + NBA Design

---

## OBJETIVO

Eliminar dualidad rules vs LLM y preparar el sistema para decisión global (NBA)

---

## PROBLEMA INICIAL

- duplicados en recommendations
- múltiples fuentes sin coordinación
- incoherencia estructural
- falta de control sobre el output del sistema

---

## ACCIONES REALIZADAS

### 1. Modelo

- añadido campo `source` en AIRecommendation
- valores:
  - rules
  - llm
  - merged

---

### 2. LLM Integration

- todas las recommendations generadas por LLM → source="llm"

---

### 3. Merge Engine

Implementado:

- merge.py
- merge_runtime.py

Capacidades:

- deduplicación por type + scope
- prioridad rules
- enriquecimiento con LLM
- salida única

---

### 4. Integración en pipeline

- hook en:
  apps/inferences/services.py

Flujo:

rules → llm → merge → persistencia

---

### 5. Persistencia

- recommendations originales → dismissed
- recommendation final → merged + new

---

### 6. Validación

- tests OK
- system check OK
- smoke test OK

---

### 7. Micro-Debriefing

Definido diseño completo de:

Next Best Action Engine (NBA)

---

## DECISIONES CLAVE NBA

- unidad: recommendations
- output: 1 única acción global
- ejecución: runtime (no persistido)

---

### Scoring

score = confidence + urgency + type_weight

---

### Urgency

- basada en reglas
- no LLM

---

### Type Weight

- hardcoded V1

---

### Explainability

- fuera de alcance (V1)

---

## RESULTADO

Sistema:

- coherente
- determinista
- sin duplicados
- listo para decisión global

---

## ESTADO FINAL

Merge Layer V1: COMPLETADA  
NBA Engine: DISEÑADO (pendiente implementación)

