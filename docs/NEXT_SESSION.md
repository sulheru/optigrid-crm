# NEXT SESSION

Implementar CRM Update Engine V2.3 — Trace Schema Normalization.

## Contexto
El Rule Engine ya está operativo, las condiciones declarativas mínimas están establecidas y `RULE_TRACE` ya distingue entre evaluación, selección, descarte y efecto final.

Actualmente el sistema soporta:

- reglas desacopladas
- versionado
- replay
- diff
- trazabilidad mejorada
- condiciones declarativas simples

Condiciones activas:

- `always_true`
- `inference_exists`

## Problema actual
El trace ya es semánticamente claro, pero sigue siendo un `dict` libre.

Eso no rompe nada, pero deja abierta la puerta a:

- divergencias futuras entre entradas del trace
- crecimiento desordenado del esquema
- mayor dificultad para consumirlo desde tooling o UI

## Objetivo
Normalizar el esquema interno de `RULE_TRACE` sin cambiar el comportamiento funcional del motor.

## Alcance
- definir estructura interna consistente para entradas del trace
- conservar compatibilidad con logs y tests actuales
- mantener replay y diff sin cambios funcionales
- preparar una base mejor para explainability futura

## Importante
- no introducir LLM
- no introducir UI
- no introducir persistencia nueva
- no cambiar outputs del motor
- no sobre-ingeniería

## Algoritmo de trabajo

Briefing
- validar la estructura actual antes de tocar el esquema

Ciclo de implementación
1. recoger contexto real
2. normalizar mínimo viable
3. probar
4. iterar

Debriefing
- resumen de sesión
- próximos pasos

## Formato de respuesta
Introducción breve
código
siguiente paso
