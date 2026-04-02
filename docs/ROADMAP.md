# ROADMAP — OptiGrid CRM

## Estado actual
Fase activa: CRM Update Engine V2.x

El sistema dispone ya de:

- Rule Engine desacoplado
- versionado de reglas
- replay de decisiones
- diff entre versiones
- capa de condiciones declarativas mínima operativa
- trazabilidad semánticamente refinada
- trazabilidad estructurada mínima mediante `event_type`
- normalización del trace y capa helper/query

## Estado de la fase V2.x
Completado:

- V2 — Rule Engine desacoplado
- V2.1 — Declarative Conditions Layer mínima
- V2.2 — Trace Semantics Refinement
- V2.3 — Structured Trace & Decision Model
- V2.4 — Trace Normalization & Query Layer

Actualmente soportado en condiciones declarativas:

- `always_true`
- `inference_exists`

## Objetivo inmediato siguiente
Convertir el trace ya normalizado en explainability consumible y preparar la primera UI útil del motor.

Línea prioritaria recomendada:

### V2.5 — Explainability Layer
Objetivo:
traducir `RULE_TRACE` a explicación determinista y legible para humanos.

Puntos previstos:

- introducir `explain_trace(trace) -> List[str]`
- explicar:
  - reglas seleccionadas
  - reglas descartadas
  - motivo de descarte
  - efecto final
- reutilizar helpers existentes
- no modificar el comportamiento del motor
- preparar consumo por Chat Console y UI

### V2.6 — Presentation Payload for Decision UI
Objetivo:
exponer un payload estable y renderizable para la primera pantalla de supervisión.

Puntos previstos:

- definir estructura mínima de presentación
- incluir:
  - selected_rules
  - discarded_rules
  - final_effect
  - explanation_lines
- mantener separación:
  - motor
  - explainability
  - presentación

### Primera UI recomendada — Email Decision Detail
Objetivo:
mostrar de forma clara cómo se tomó la decisión sobre un email concreto.

La pantalla debería enseñar:

- propuesta resultante
- reglas seleccionadas
- reglas descartadas
- explicación legible
- efecto final

## No hacer todavía
- no introducir LLM en el motor de reglas
- no introducir UI global de dashboard de decisiones
- no introducir editor visual de reglas
- no introducir persistencia nueva del trace
- no tipar en exceso el trace todavía
- no construir CRUD-first UI

## Criterio de avance
La fase V2.x avanzará correctamente si:

- las reglas siguen siendo reproducibles
- el comportamiento sigue siendo trazable
- el trace puede explicarse de forma legible
- la primera UI muestra decisiones reales sin heurísticas frágiles
- la complejidad del motor se mantiene baja
