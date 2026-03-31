# CHANGELOG

## 2026-03-31 — Identity & Corporation Layer V1 estabilizado

### Hecho
- Se consolida `OperatingOrganization` como corporation canónica.
- Se mantiene `MailboxAccount` como entidad canónica de buzón.
- Se estabilizan los modelos de tenancy:
  - `OperatingOrganization`
  - `CorporateDomain`
  - `Identity`
  - `CorporateMembership`
  - `MailboxAccount`
- Se deja operativa la resolución:
  - `email -> domain -> CorporateDomain -> OperatingOrganization`
- Se corrige `apps/simulated_personas/services/prompt_builder.py`:
  - uso correcto de `mailbox_account.email`
- Se corrige `apps/emailing/services/smll_bootstrap.py`:
  - simulation lab alineada con `CorporateDomain`
  - dominio `simulation.local` asegurado
- Se refuerza `apps/emailing/services/provider_router.py`:
  - resolución segura de mailbox
  - sin inferencia peligrosa desde remitente externo
- Se valida la fase con:
  - `python manage.py test apps.tenancy apps.simulated_personas apps.emailing`
  - `python manage.py check`

### Resultado
- 25 tests OK
- system check OK
- tenancy + SMLL + provider layer consistentes

### Pendiente
- crear `apps.crm_update_engine.entrypoints.process_email`
- persistir tenant/mailbox scope en emailing
- limpiar drift de migraciones no relacionadas (`knowledge`, futuros ajustes tenancy)
