# CHANGELOG

## 2026-04-02 — CRM Update Engine V2.3 — Structured Trace & Decision Model

Se estructura `RULE_TRACE` sin cambiar el comportamiento funcional del motor.

### Cambios realizados
- se añade `event_type` a las entradas del trace
- se conserva compatibilidad con la estructura previa:
  - `rule`
  - `matched`
  - `conditions`
  - `priority`
- se mantienen los campos semánticos introducidos en V2.2:
  - `condition_match`
  - `rule_selected`
  - `rule_discarded`
  - `discard_reason`
  - `final_effect`
- se mantiene el hard stop tras regla final
- no se modifica `create_basic_proposal`

### Resultado
- el motor sigue siendo determinista
- la trazabilidad gana estructura explícita
- replay sigue operativo
- diff sigue operativo
- los tests del motor y de integración siguen en verde

### Observación pendiente
`event_type` ya permite distinguir selección, descarte y efecto final, pero todavía conviene refinar el modelo y añadir helpers de consulta del trace.
