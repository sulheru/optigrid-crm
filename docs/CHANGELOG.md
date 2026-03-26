# CHANGELOG

## 2026-03-26 — NBA ENGINE CONSOLIDATION

### Added

- NBA Engine como motor canónico
- Explainability:
  - get_score_breakdown
  - get_next_best_action_explained

### Changed

- Eliminada dualidad conceptual:
  - ranking_engine deja de ser fuente de verdad
- Dashboard usa únicamente NBA Engine
- Tests alineados con modelo real

### Fixed

- mismatch entre tests y modelo (confidence NOT NULL)
- eliminación de campos inexistentes en tests
- estabilidad del dashboard

### Architectural

- separación clara:
  - IA (confidence)
  - sistema (scoring runtime)
- scoring no persistido

### Result

Sistema pasa de:
- múltiples criterios de priorización

a:
- un único motor de decisión coherente
