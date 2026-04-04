# Changelog

## [Core Operational Closure]

### Añadido
- Execution Engine completo
- ExternalActionIntent pipeline
- Email draft generation (sandbox-safe)
- Idempotencia en ejecución
- Provider abstraction operativa

### Corregido
- Eliminada dependencia obligatoria de mailbox_account
- Tests alineados con modelo de dominio
- Validaciones trasladadas a provider layer

### Validado
- 15 tests (core)
- 21 tests (extended)
- System check sin errores

### Decisiones estructurales
- operating_organization obligatorio
- mailbox_account opcional
- arquitectura event-driven consolidada
- separación clara: core vs entorno

### Estado
Core completamente cerrado para operación controlada
