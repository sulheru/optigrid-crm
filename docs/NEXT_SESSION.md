# NEXT SESSION

Implementar CRM Update Engine V2.5 — Explainability Layer.

## Contexto
El Rule Engine ya está operativo y estable.

`RULE_TRACE` ya dispone de:

- semántica de selección y descarte
- `event_type` refinado
- helpers de consulta

Actualmente el sistema soporta:

- reglas desacopladas
- versionado
- replay
- diff
- trazabilidad semántica
- trazabilidad estructurada
- query layer sobre trace

Condiciones activas:

- `always_true`
- `inference_exists`

## Problema actual
El motor ya decide bien y el trace ya es consumible, pero aún no existe una capa que traduzca esas decisiones a una explicación legible para humanos.

Eso bloquea una UI realmente útil y limita el consumo por Chat Console.

## Objetivo
Construir una Explainability Layer determinista sobre `RULE_TRACE`.

## Alcance
- introducir:
  - `explain_trace(trace) -> List[str]`
- explicar:
  - reglas seleccionadas
  - reglas descartadas
  - motivo del descarte
  - efecto final
- reutilizar helpers existentes
- no reparsear el trace manualmente desde cero
- preparar base para el payload de presentación de la primera UI

## Importante
- no modificar `evaluate_rules`
- no modificar `create_basic_proposal`
- no cambiar outputs funcionales del motor
- no introducir LLM
- no introducir persistencia nueva
- no sobre-ingeniería

## Decisión de producto/UI ya tomada
La primera UI útil será:

### Email Decision Detail

No hacer todavía:

- dashboard global
- editor de reglas
- UI genérica del sistema
- CRUD pesado

## Algoritmo de trabajo

Briefing
- validar estructura real de trace y helpers

Ciclo de implementación
1. construir explainability mínima
2. probar
3. definir payload de presentación mínimo
4. iterar

Debriefing
- resumen de sesión
- preparar siguiente paso hacia UI

## Formato de respuesta
Introducción breve
código
siguiente paso
