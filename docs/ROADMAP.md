# ROADMAP — OptiGrid CRM
Actualizado: 2026-04-05

## Estado global
El proyecto ha superado una fase importante de saneamiento estructural y estabilización del núcleo de tenancy/identity.

## Fases

### Fase A — Core Closure
Estado: completado funcionalmente
Incluye:
- rule engine
- rule trace
- explainability
- decision output
- execution policy
- provider abstraction inicial

### Fase B — EIL Foundation
Estado: completada en esta sesión
Incluye:
- `OperatingOrganization`
- `CorporateDomain`
- `Identity`
- `CorporateMembership`
- `MailboxAccount`
- `PublicEmailDomain`
- `EmailIdentity`
- seed de dominios públicos
- `domain_resolution.py`
- integración inicial en ingest y entrypoints

### Fase C — EIL Integration Deepening
Estado: siguiente fase
Pendiente:
- extender EIL a más consumers
- revisar modelos de correo
- consolidar persistencia de organización/identidad
- clarificar relación operativa entre `MailboxAccount` y `EmailIdentity`

### Fase D — Entity Manager
Estado: pendiente, pero ya desbloqueado conceptualmente
Dependencia:
- cerrar mejor integración EIL primero

### Fase E — SMLL Expansion
Estado: parcialmente operativo
Ya validado:
- runtime básico
- bootstrap
- integración mínima
Pendiente:
- aprovechar EIL más profundamente en simulación y flujos de correo

### Fase F — Producción controlada
Pendiente
Incluye:
- mayor hardening
- convergencia de capas legacy y nuevas
- revisión de políticas de migración y versionado
- consolidación de provider/runtime

## Prioridad inmediata
1. EIL Integration Deepening
2. Entity Manager
3. expansión funcional posterior

## Nota estratégica
La decisión correcta ahora es evolución incremental:
- coexistencia controlada
- refactorización por capas
- evitar sustituciones masivas de conceptos legacy
