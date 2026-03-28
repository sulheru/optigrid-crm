# CHANGELOG

## 2026-03-27 — External Actions Pipeline

### Added

- Approval service
- Dispatcher limpio y no recursivo
- Email provider stub
- Tests completos:
  - approval flow
  - dispatch con y sin approval
  - idempotencia
  - manejo de errores

### Fixed

- Bug crítico de rollback en transacciones (failure-safe execution)
- Introspección incorrecta de campos
- Inconsistencias en execution_status

### Architectural Decisions

- Separación estricta create vs dispatch
- Schema-tolerant dispatcher
- Failure-safe execution (doble transacción)
- Idempotencia obligatoria

### Status

✔ Stable
✔ Tested
✔ Ready for next phase

