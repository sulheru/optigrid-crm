# CHANGELOG

## 2026-04-01 — CRM Update Engine V2.1 — Declarative Conditions Layer

Se completa la primera capa declarativa de condiciones del Rule Engine.

### Cambios realizados
- se sustituye la evaluación directa de condiciones Python por un evaluator declarativo
- se mantiene compatibilidad temporal con condiciones legacy tipo callable
- se introducen condiciones declarativas mínimas:
  - `always_true`
  - `inference_exists`
- se refactorizan `rules_v1.py` y `rules_v2.py` para usar condiciones declarativas
- `rule_engine.py` pasa a evaluar condiciones mediante `evaluate_condition`
- se endurece el manejo de condiciones inválidas o vacías
- se añaden tests reales en `apps/updates/tests.py`

### Resultado
- el comportamiento actual del motor se mantiene
- replay sigue operativo
- diff sigue operativo
- `create_basic_proposal` sigue operativo
- `RULE_TRACE` sigue operativo
- los tests del motor y la integración principal quedan en verde

### Observación pendiente
La semántica de `RULE_TRACE` todavía puede afinarse para distinguir mejor entre:

- regla que cumple condiciones
- regla finalmente aplicada
- regla descartada por final/conflicto
