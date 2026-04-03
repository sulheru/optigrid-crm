# CHANGELOG

## 2026-04-03 — Core Operational Closure (Phase 1)

### Added

- ExecutionRequest (modelo de ejecución explícito)
- ExecutionEngine mínimo funcional
- ExecutionResult estructurado
- soporte de mailbox_account en execution
- resolve_mail_account_ref desde BD

### Changed

- prepare_provider_draft ahora soporta mailbox_account
- execution desacoplada de recommendation
- reply_strategy migrado a execution_engine

### Extended

- OutboundEmail:
  - operating_organization
  - mailbox_account

- InboundEmail:
  - operating_organization
  - mailbox_account

### Fixed

- eliminación parcial de identidad heurística en ejecución
- providers ahora reciben identidad correcta

### Tests

- resolución de mailbox desde BD
- ejecución de drafts
- integración execution_engine + provider

### Impacto

Cambio estructural mayor:

👉 separación explícita entre decisión y acción

Habilita:

- control de ejecución
- automatización futura segura
- arquitectura de plugins

