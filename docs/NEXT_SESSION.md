# NEXT SESSION

Implementar CRM Update Engine V2.4 — Trace Normalization & Query Layer.

## Contexto
El Rule Engine ya está operativo, las condiciones declarativas mínimas están establecidas y `RULE_TRACE` ya distingue selección, descarte y efecto final mediante `event_type`.

Actualmente el sistema soporta:

- reglas desacopladas
- versionado
- replay
- diff
- trazabilidad semántica
- trazabilidad estructurada mínima

Condiciones activas:

- `always_true`
- `inference_exists`

## Problema actual
El trace ya es consumible de forma más clara, pero `event_type` sigue siendo todavía demasiado genérico y no existen helpers para consultar el modelo de decisión.

## Objetivo
Refinar el modelo del trace y habilitar acceso estructurado sin cambiar el comportamiento funcional del motor.

## Alcance
- refinar semánticamente `event_type` si se puede hacer sin romper compatibilidad
- introducir helpers de lectura del trace
- conservar compatibilidad con logs y tests actuales
- mantener replay y diff sin cambios funcionales
- preparar base mejor para consumo desde Chat Console

## Importante
- no introducir LLM
- no introducir UI
- no introducir persistencia nueva
- no cambiar outputs funcionales del motor
- no sobre-ingeniería

## Algoritmo de trabajo

Briefing
- validar la estructura real antes de tocar helpers o normalización

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
