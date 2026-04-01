# ROADMAP — OptiGrid CRM

## Estado actual
Fase activa: CRM Update Engine V2.x

El sistema dispone ya de:

- Rule Engine desacoplado
- versionado de reglas
- loader dinámico
- replay de decisiones
- diff entre versiones
- trazabilidad mediante RULE_TRACE
- capa de condiciones declarativas mínima operativa

## Estado de la fase V2.x
Completado:

- V2 — Rule Engine desacoplado
- V2.1 — Declarative Conditions Layer mínima

Actualmente soportado en condiciones declarativas:

- `always_true`
- `inference_exists`

## Objetivo inmediato siguiente
Refinar la capa declarativa sin aumentar complejidad innecesaria.

Línea prioritaria recomendada:

### V2.2 — Trace Semantics Refinement
Objetivo:
hacer que `RULE_TRACE` distinga con claridad entre:

- regla que cumple condiciones
- regla aplicada efectivamente
- regla descartada por conflicto
- regla descartada por existencia de regla final

### V2.3 — Rule Schema Normalization
Objetivo:
reducir ambigüedad interna del esquema de reglas.

Puntos previstos:

- unificar `final=True` y `outcome="final"`
- mantener compatibilidad con replay y diff
- dejar esquema preparado para persistencia futura

## No hacer todavía
- no introducir LLM en el motor de reglas
- no introducir UI de edición de reglas
- no introducir DSL compleja
- no añadir tipos de condición sin caso real

## Criterio de avance
La fase V2.x avanzará correctamente si:

- las reglas siguen siendo reproducibles
- el comportamiento sigue siendo trazable
- las condiciones pueden serializarse
- la complejidad del motor se mantiene baja
