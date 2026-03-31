# NEXT SESSION — CRM UPDATE ENGINE V2

## Objetivo

Introducir un Rule Engine para desacoplar la lógica de negocio.

## Problema actual

La lógica está hardcodeada:

if has_pricing_signal:
    proposal_type = "prepare_pricing_response"

Esto limita:
- escalabilidad
- configurabilidad
- integración futura con LLM

## Objetivo técnico

Crear un sistema:

Signals → Rules → Proposals

## Alcance

- Definir estructura RULES
- Implementar rule evaluator
- Integrar con create_basic_proposal
- Mantener compatibilidad con tests actuales

## No hacer

- No introducir UI
- No introducir LLM todavía
- No romper pipeline existente

## Resultado esperado

- Lógica desacoplada
- Sistema extensible
- Base preparada para IA

