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

---

## 2026-03-25 — NBA Engine V1 (Partial Implementation)

### Added

- creado `apps/recommendations/nba.py`
- añadido scoring runtime para recommendations
- añadidas reglas simples de urgencia V1
- añadidos pesos por tipo
- creada selección de una única recommendation global
- creado `apps/recommendations/tests_nba.py`
- añadido bloque dashboard "What should you do now"

### Validated

- `manage.py check` OK
- tests de `apps.recommendations` OK
- dashboard vuelve a cargar correctamente

### Fixed During Session

- corregida corrupción de import en `apps/dashboard_views.py`
- corregido bloque de imports roto
- restaurada carga correcta del dashboard

### Architectural Finding

- existe dualidad entre:
  - `apps/recommendations/nba.py`
  - `apps/recommendations/ranking_engine.py`

### Current Status

- NBA V1 estable
- integración funcional
- consolidación canónica pendiente
