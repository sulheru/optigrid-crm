# CHANGELOG

## 2026-04-02 — CRM Update Engine V2.4 — Trace Normalization & Query Layer

Se refina la expresividad de `RULE_TRACE` y se introduce una capa helper/query sin cambiar el comportamiento funcional del motor.

### Cambios realizados
- se refina `event_type` en descartes
- se distinguen explícitamente:
  - `rule_discard_condition_failed`
  - `rule_discard_shadowed`
  - `rule_discard_conflict`
- se mantiene compatibilidad semántica hacia atrás mediante:
  - `discard_reason`
  - `rule_selected`
  - `rule_discarded`
  - `final_effect`
- se introducen helpers de consulta:
  - `get_selected_rules(trace)`
  - `get_discarded_rules(trace)`
  - `get_final_effect(trace)`
- no se modifica `create_basic_proposal`
- no se modifica replay
- no se modifica diff
- no se altera el comportamiento del Rule Engine

### Resultado
- el motor sigue siendo determinista
- el trace gana expresividad real
- el trace pasa a ser consumible como API interna
- la base para explainability queda preparada
- la base para Chat Console y futura UI queda preparada

### Observación pendiente
La siguiente capa natural ya no es del motor, sino de explainability:

- traducir trace a explicación legible
- preparar payload de presentación
- construir primera UI útil sobre decisiones reales
