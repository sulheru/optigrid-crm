# NEXT SESSION — OptiGrid CRM

## Fase

PROVIDER ABSTRACTION LAYER — INICIO

## Objetivo

Introducir capa de providers sin romper el sistema actual.

## Tareas

1. Definir interfaces:
   - MailProvider
   - LLMProvider
   - CalendarProvider

2. Crear wrappers:
   - EmbeddedMailProvider
   - M365MailProvider (wrapper sobre graph_client)
   - EmbeddedLLMProvider
   - GeminiLLMProvider (wrapper sobre llm_backends)

3. Wiring:
   - conectar providers en execution_adapters
   - introducir flags en settings

4. Validación:
   - no romper tests
   - mantener comportamiento actual

## Reglas

- NO implementar integraciones completas
- NO romper execution
- NO refactor innecesario

## Resultado esperado

Sistema con providers intercambiables listo para integraciones reales.
