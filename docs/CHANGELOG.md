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

## [2026-04-04] — Entity & Identity Layer (EIL) Design

### Added

- Diseño completo de Entity & Identity Layer (EIL)
- Definición de OperatingOrganization como tenant canónico
- Modelo de EmailIdentity como raíz de identidad
- Introducción de Domain como entidad explícita
- Separación Organization vs Company
- Modelo Contact híbrido (persona / rol)
- Candidate layer:
  - CompanyCandidate
  - ContactCandidate
- Base de monetización en OperatingOrganization
- Contexto LLM por organización:
  - description
  - llm_context_summary

### SMLL

- Definición de sandbox organizations
- Introducción de dominios `.sim`
- Aislamiento total entre entorno real y simulado
- Relación sandbox ↔ organización real (solo perfil, no identidad)

### Architecture

- Formalización del sistema multi-tenant
- Definición de ownership completo del CRM
- Preparación para resolución de identidad en ingestión

### Future-ready

- Base para automatizaciones aprendidas:
  - modelo conceptual
  - control mediante switch
- Preparación para verificación de dominio (no implementado)

