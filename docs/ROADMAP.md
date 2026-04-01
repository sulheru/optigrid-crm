# ROADMAP — OptiGrid CRM

## Estado actual
Fase activa: CRM Update Engine V2.x

El sistema dispone ya de:

- Rule Engine desacoplado
- versionado de reglas
- replay de decisiones
- diff entre versiones
- capa de condiciones declarativas mínima operativa
- trazabilidad semánticamente refinada mediante `RULE_TRACE`

## Estado de la fase V2.x
Completado:

- V2 — Rule Engine desacoplado
- V2.1 — Declarative Conditions Layer mínima
- V2.2 — Trace Semantics Refinement

Actualmente soportado en condiciones declarativas:

- `always_true`
- `inference_exists`

## Objetivo inmediato siguiente
Refinar el esquema interno del motor sin aumentar complejidad innecesaria.

Línea prioritaria recomendada:

### V2.3 — Trace Schema Normalization
Objetivo:
normalizar la estructura de `RULE_TRACE` para que el trace deje de crecer como `dict` libre y gane consistencia interna.

Puntos previstos:

- unificar forma de las entradas del trace
- mantener compatibilidad con replay y diff
- preparar base para explainability futura

### V2.4 — Rule Schema Normalization
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
- no introducir persistencia de reglas

## Criterio de avance
La fase V2.x avanzará correctamente si:

- las reglas siguen siendo reproducibles
- el comportamiento sigue siendo trazable
- las condiciones pueden serializarse
- el trace puede explicarse con claridad
- la complejidad del motor se mantiene baja
