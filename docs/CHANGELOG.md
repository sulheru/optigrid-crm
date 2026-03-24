# CHANGELOG

## 2026-03-24 — Recommendation Merge Layer V1

[contenido previo...]

---

## 2026-03-24 — NBA Engine Design (Pre-Implementation)

### Added (Design Decisions)

- definición de Next Best Action (NBA)
- unidad de ranking: Recommendations
- ejecución: runtime (no persistido)
- output: 1 acción global

### Scoring Model

score = confidence + urgency + type_weight

### Urgency
- basada en reglas
- no LLM

### Type Weight
- hardcoded en V1

### Constraints
- sin explainability
- sin ML
- sin persistencia

### Objective
convertir el sistema en decisor operativo

