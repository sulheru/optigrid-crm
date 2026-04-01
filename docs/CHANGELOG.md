# CHANGELOG

## 2026-04-01 — CRM Update Engine V2.2 — Trace Semantics Refinement

Se refina la semántica de `RULE_TRACE` sin cambiar los outputs funcionales del motor.

### Cambios realizados
- se enriquece el trace con campos semánticos explícitos:
  - `condition_match`
  - `rule_selected`
  - `rule_discarded`
  - `discard_reason`
  - `final_effect`
- se mantiene compatibilidad con la estructura previa del trace:
  - `rule`
  - `matched`
  - `conditions`
  - `priority`
- se corrige una incoherencia del motor:
  - una regla marcada como final ahora bloquea correctamente reglas posteriores
- se añade cobertura de tests para la nueva semántica del trace

### Resultado
- el comportamiento funcional del motor se mantiene
- `create_basic_proposal` sigue operativo sin cambios
- replay sigue operativo
- diff sigue operativo
- los tests del motor y la integración principal siguen en verde

### Observación pendiente
La semántica del trace ya es clara, pero el esquema sigue siendo un `dict` libre. El siguiente paso lógico es normalizar el modelo interno del trace sin introducir complejidad innecesaria.
