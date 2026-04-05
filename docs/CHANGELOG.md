# CHANGELOG

## 2026-04-05 — EIL Implementation (Phase 1)
### Añadido
- introducción de `EmailIdentity`
- introducción de `PublicEmailDomain`
- servicios EIL en `apps/tenancy/services/domain_resolution.py`
- seed de dominios públicos mediante migración
- integración inicial de resolución EIL en:
  - `services/email_ingest.py`
  - `apps/crm_update_engine/entrypoints.py`

### Mantenido
- `OperatingOrganization`
- `CorporateDomain`
- `Identity`
- `CorporateMembership`
- `MailboxAccount`

### Refactorizado
- `apps/tenancy/models.py`
- `apps/tenancy/admin.py`
- `apps/emailing/services/provider_router.py`
- `apps/emailing/services/smll_bootstrap.py`

### Validado
Suites en verde:
- `apps.tenancy.tests_identity`
- `apps.simulated_personas.tests_runtime`
- `apps.emailing.tests_smll_integration`
- `apps.recommendations.tests_execution_engine`

### Resultado
EIL queda introducido y operativo a nivel fundacional sin romper la capa legacy consumida por SMLL, runtime de mail y execution engine.
