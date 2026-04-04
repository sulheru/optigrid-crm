Vamos a trabajar sobre OptiGrid CRM — EIL Implementation (Phase 1).

Contexto:

El diseño de Entity & Identity Layer está completamente definido.

Existe:

- modelo conceptual completo
- decisiones cerradas sobre:
  - tenancy
  - email identity
  - CRM entities
  - candidate layer
  - SMLL sandbox
  - monetización

Objetivo:

Implementar EIL en Django.

Alcance:

- models.py completos
- relaciones entre entidades
- campos mínimos necesarios
- migraciones

Servicios mínimos:

- resolve_email_identity(email)
- resolve_organization(email_identity)
- create_provisional_organization(domain)

Restricciones:

- no login
- no permisos
- no UI
- no providers externos aún

Principios:

- determinismo
- simplicidad
- no sobre-ingeniería
- preparado para inbound automático

Criterio de éxito:

- se puede procesar un email y asignarlo a una organización
- no existen datos sin organization
- el sistema soporta multi-tenant desde el día 1

