# HANDOFF CURRENT — CRM UPDATE ENGINE (STABLE)

## Estado general

El pipeline CRM Update Engine está completamente funcional y validado mediante tests de integración.

## Pipeline actual

email
→ FactRecord
→ InferenceRecord
→ CRMUpdateProposal
→ AIRecommendation

## Características clave

- Pipeline determinista y ordenado
- Idempotencia garantizada mediante get_or_create
- Dependencia semántica entre capas:
  - Inference → Proposal
- Señales implementadas:
  - pricing_interest_signal → prepare_pricing_response

## Entry point

apps.crm_update_engine.entrypoints.process_email(email)

## Cobertura de tests

- Idempotencia del pipeline
- Detección de señales de pricing
- Generación de proposal específica

Todos los tests pasan correctamente.

## Limitaciones actuales

- Lógica de negocio hardcodeada (if/else)
- Sin motor de reglas
- Sin LLM
- Sin configuración dinámica

## Estado

🟢 ESTABLE — listo para evolucionar
