# HANDOFF CURRENT — CRM Update Engine V2.5

## Estado actual

El CRM Update Engine ha evolucionado a V2.5 con éxito.

El sistema es ahora:

- determinista
- desacoplado mediante Rule Engine
- declarativo en condiciones
- trazable semántica y estructuralmente
- consultable mediante helpers sobre `RULE_TRACE`
- explicable mediante una capa determinista separada del motor

## Mejora clave introducida

Se ha añadido una Explainability Layer sobre `RULE_TRACE`.

Nueva función disponible:

- `explain_trace(trace) -> List[str]`

La explainability se apoya en la capa helper/query ya existente:

- `get_selected_rules(trace)`
- `get_discarded_rules(trace)`
- `get_final_effect(trace)`

## Propiedades garantizadas

- compatibilidad total hacia atrás
- sin cambios en comportamiento
- `evaluate_rules` intacto
- `create_basic_proposal` intacto
- replay sin impacto funcional
- diff sin impacto funcional
- tests del módulo en verde
- tests de integración del emailing en verde

## Qué explica ya el sistema

La capa V2.5 ya puede explicar de forma legible:

- por qué se seleccionó una regla
- por qué se descartó una regla
- si una regla fue descartada por condición fallida
- si una regla fue descartada por conflicto
- si una regla fue descartada por shadowing
- cuál fue el efecto final del motor

## Estado arquitectónico

La cadena arquitectónica queda así:

1. motor de reglas
2. `RULE_TRACE`
3. helpers/query layer
4. explainability

Esto deja el sistema preparado para:

- consumo por Chat Console
- payload de salida estable
- primera UI útil basada en decisiones reales

## Limitaciones actuales

- aún no existe un payload unificado listo para UI
- explainability devuelve texto, pero no una estructura de presentación completa
- el trace sigue siendo lista de dicts
- todavía no existe vista de detalle de decisión

## Decisión tomada para la siguiente fase

La siguiente fase será:

### V2.6 — Decision Output Layer

Y la primera UI objetivo seguirá siendo:

### Email Decision Detail

Orden de trabajo decidido:

1. output estructurado
2. presentación/UI
3. consumo por Chat Console

## Qué no haremos todavía

- no tocar `evaluate_rules`
- no reabrir semántica del motor
- no introducir LLM
- no introducir persistencia nueva
- no construir dashboard global
- no construir editor de reglas
- no hacer UI genérica antes del payload estable
