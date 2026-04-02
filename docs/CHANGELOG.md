# CHANGELOG

## 2026-04-02 — CRM Update Engine V2.5 — Explainability Layer

Se introduce una capa de explainability determinista sobre `RULE_TRACE` sin modificar el comportamiento funcional del motor.

### Cambios realizados
- se añade `apps/updates/explainability.py`
- se introduce:
  - `explain_trace(trace) -> List[str]`
- la explainability:
  - reutiliza `get_selected_rules(trace)`
  - reutiliza `get_discarded_rules(trace)`
  - reutiliza `get_final_effect(trace)`
- se generan explicaciones legibles para:
  - reglas seleccionadas
  - reglas descartadas
  - efecto final
- se mantiene separación estricta:
  - motor != explicación
- no se modifica `evaluate_rules`
- no se modifica `create_basic_proposal`
- no se introduce LLM
- no se introduce persistencia
- se amplían tests del módulo `apps.updates`
- se valida compatibilidad con tests de integración del CRM Update Engine

### Resultado
- el motor sigue siendo determinista
- el trace sigue siendo la fuente de verdad
- las decisiones ya son explicables en lenguaje legible
- Chat Console queda más cerca de poder consumir decisiones reales
- la base para una UI útil queda preparada

### Observación pendiente
La siguiente capa natural ya no es del motor ni de explainability, sino del output estructurado para presentación:

- construir `build_decision_output(trace)`
- exponer un payload estable
- preparar la primera UI útil sobre decisiones reales

## V2.6 — Decision Output Layer

### Added
- build_decision_output(trace)

### Features
- selected_rules
- discarded_rules
- final_effect
- explanation

### Improvements
- Output normalizado para consumo UI
- Separación estricta entre capas

### Fixes
- Alineación de tests con RULE_TRACE real

### Status
- Tests passing
- Ready for UI consumption
