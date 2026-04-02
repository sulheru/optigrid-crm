# NEXT SESSION

Implementar CRM Update Engine V2.6 — Decision Output Layer.

## Contexto
El Rule Engine ya está operativo y estable.

`RULE_TRACE` ya dispone de:

- semántica de selección y descarte
- `event_type` refinado
- helpers de consulta

Además, ahora el sistema ya soporta:

- explainability determinista sobre trace

Actualmente el sistema dispone de:

- reglas desacopladas
- versionado
- replay
- diff
- trazabilidad semántica
- query layer sobre trace
- explainability legible

Condiciones activas:

- `always_true`
- `inference_exists`

## Problema actual
El sistema ya decide bien y ya explica bien, pero aún no expone una estructura unificada y estable lista para consumo por UI o Chat Console.

Eso bloquea la primera capa real de presentación.

## Objetivo
Construir una capa de salida estructurada sobre trace + helpers + explainability.

## Alcance
- introducir:
  - `build_decision_output(trace) -> Dict`
- incluir en el output:
  - `selected_rules`
  - `discarded_rules`
  - `final_effect`
  - `explanation`
- reutilizar:
  - `get_selected_rules`
  - `get_discarded_rules`
  - `get_final_effect`
  - `explain_trace`
- no duplicar lógica
- no reparsear el motor
- preparar base directa para UI y Chat Console

## Importante
- no modificar `evaluate_rules`
- no modificar `create_basic_proposal`
- no cambiar outputs funcionales del motor
- no tocar explainability salvo necesidad mínima de integración
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
- validar estructura real de trace, helpers y explainability

Ciclo de implementación
1. construir decision output layer mínima
2. probar
3. validar consistencia con explainability
4. dejar payload listo para presentación

Debriefing
- resumir V2.6
- preparar salto a la primera UI útil

## Formato de respuesta
Introducción breve
código
siguiente paso
