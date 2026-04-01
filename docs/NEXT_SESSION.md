# NEXT SESSION

Implementar CRM Update Engine V2.2 — Trace Semantics Refinement.

## Contexto
El Rule Engine ya está operativo y la capa declarativa mínima de condiciones también.

Actualmente el sistema soporta:

- reglas desacopladas
- versionado
- replay
- diff
- trazabilidad
- condiciones declarativas simples

Condiciones activas:

- `always_true`
- `inference_exists`

## Problema actual
`RULE_TRACE` todavía no expresa con suficiente claridad la diferencia entre:

- regla que cumple condiciones
- regla aplicada finalmente
- regla descartada por conflicto
- regla descartada por presencia de regla final

Esto no rompe el sistema, pero reduce calidad de trazabilidad y auditabilidad.

## Objetivo
Refinar la semántica del trace sin cambiar el comportamiento funcional del motor.

## Alcance
- revisar estructura de entradas del trace
- distinguir evaluación de condiciones frente a aplicación real
- registrar de forma explícita los motivos de descarte
- mantener compatibilidad con:
  - `create_basic_proposal`
  - replay
  - diff
  - tests actuales

## Importante
- no introducir LLM
- no introducir UI
- no introducir persistencia de reglas
- no sobre-ingeniería
- no cambiar el comportamiento observable del motor salvo en el contenido del trace

## Algoritmo de trabajo

Briefing
- validar el enfoque antes de tocar el motor

Ciclo de implementación
1. recoger contexto real
2. implementar mínimo viable
3. probar
4. iterar

Debriefing
- resumen de sesión
- próximos pasos

## Formato de respuesta
Introducción breve
código
siguiente paso
