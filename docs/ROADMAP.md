# ROADMAP — OptiGrid CRM

## Estado actual
Fase activa: CRM Update Engine V2.x

El sistema dispone ya de:

- Rule Engine desacoplado
- versionado de reglas
- replay de decisiones
- diff entre versiones
- condiciones declarativas mínimas operativas
- trazabilidad semánticamente refinada
- trace estructurado y consultable
- Explainability Layer determinista

## Estado de la fase V2.x
Completado:

- V2 — Rule Engine desacoplado
- V2.1 — Declarative Conditions Layer mínima
- V2.2 — Trace Semantics Refinement
- V2.3 — Structured Trace & Decision Model
- V2.4 — Trace Normalization & Query Layer
- V2.5 — Explainability Layer

Actualmente soportado en condiciones declarativas:

- `always_true`
- `inference_exists`

## Objetivo inmediato siguiente
Convertir trace + explainability en un payload estable y consumible por UI y Chat Console.

Línea prioritaria recomendada:

### V2.6 — Decision Output Layer
Objetivo:
construir una capa de salida estructurada lista para consumo por presentación.

Puntos previstos:

- introducir `build_decision_output(trace) -> Dict`
- incluir:
  - `selected_rules`
  - `discarded_rules`
  - `final_effect`
  - `explanation`
- reutilizar:
  - `get_selected_rules`
  - `get_discarded_rules`
  - `get_final_effect`
  - `explain_trace`
- mantener separación:
  - motor
  - explainability
  - output/presentación
- no modificar comportamiento del motor

### V2.7 — Presentation Layer for Email Decision Detail
Objetivo:
mostrar una primera vista útil de decisión sobre emails reales.

Puntos previstos:

- vista de detalle de decisión por email
- presentación de:
  - reglas seleccionadas
  - reglas descartadas
  - explicación legible
  - efecto final
- consumo del Decision Output Layer
- base directa para Chat Console

## No hacer todavía
- no introducir LLM en explainability
- no tocar `evaluate_rules`
- no construir dashboard global
- no construir editor visual de reglas
- no introducir persistencia nueva del trace
- no sobre-tipar todavía el trace
- no meter HTMX/UI antes del output estable

## Criterio de avance
La fase V2.x avanzará correctamente si:

- las reglas siguen siendo reproducibles
- el comportamiento sigue siendo trazable
- el trace puede explicarse de forma legible
- existe un output estable listo para UI
- la primera UI muestra decisiones reales sin heurísticas frágiles
- la complejidad del motor se mantiene baja
