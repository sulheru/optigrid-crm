# CHANGELOG

## [Session] Action Loop V1 + Operability + Tenant Scoping

### Added
- Action Loop V1 desde dashboard:
  - approve
  - dismiss
- Servicio de materialización recommendation → ExternalActionIntent
- Nueva app tenancy
- Modelo OperatingOrganization
- Modelo MailboxAccount
- Seed inicial:
  - OptiGrid IT
  - OptiGrid Simulation Lab

### Changed
- AIRecommendation ahora admite:
  - operating_organization
  - mailbox_account
- ExternalActionIntent ahora admite:
  - operating_organization
  - mailbox_account
- Action Loop propaga scoping desde recommendation a intent
- Admin de ExternalActionIntent alineado con el modelo real

### Improved
- Observabilidad real de intents
- Human-in-the-loop funcional
- Frontera de memoria por empresa operadora
- Base para varios buzones dentro del mismo tenant
- Aislamiento preparado entre tenants distintos
- Base correcta para SMLL posterior

### Fixed
- Errores del admin por campos asumidos incorrectamente
- Errores de render en lista de intents
- Errores de importación de tenancy

### Guardrails
- Sin provider real
- Sin envío real
- email.send sigue bloqueado
