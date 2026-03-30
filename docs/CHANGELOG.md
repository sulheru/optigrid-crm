# CHANGELOG

## [SMLL Integration Stabilization]

### Added
- Bootstrap automático de:
  - OperatingOrganization
  - MailboxAccount
  - SimulatedPersona
- Context injection en process_incoming_email
- Integración completa SMLL dentro de emailing pipeline

### Changed
- Eliminada dependencia implícita de mailbox en tests
- Provider Router ahora pasa:
  - operating_organization
  - mailbox_account
- Adapter respeta contrato real del engine

### Fixed
- Error crítico:
  "No existe ningún MailboxAccount activo para SMLL"
- Tests fallando por falta de datos iniciales

### Known limitations
- CRM Update Engine no implementado
- No multi-turn simulation
- No identity/corporation layer
- No UI

### Notes
El sistema ya permite simulación end-to-end sin dependencias externas.
