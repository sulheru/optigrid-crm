# CHANGELOG

## [CRM Update Engine V1 — Pipeline completo]

### Añadido
- Pipeline completo:
  - FactRecord
  - InferenceRecord
  - CRMUpdateProposal
  - AIRecommendation

### Añadido
- create_email_fact()
- create_basic_proposal()
- create_basic_email_recommendation()

### Mejorado
- Entry point ahora orquesta todo el pipeline

### Añadido
- Lógica semántica:
  - pricing_interest_signal → prepare_pricing_response

### Corregido
- Inconsistencia de source_id (string vs int)

### Validado
- Tests de integración pasan (idempotencia + pricing)

## Estado
Pipeline funcional, coherente y estable
