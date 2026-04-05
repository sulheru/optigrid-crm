# HANDOFF_CURRENT — OptiGrid CRM
Fecha: 2026-04-05
Sesión: EIL Implementation (Phase 1)

## Estado actual
La sesión ha terminado con el sistema en estado consistente y validado.

### Validado en esta sesión
- entorno Python reconstruido y operativo
- dependencias instaladas correctamente
- migraciones regeneradas y aplicadas
- `tenancy` refactorizado y estabilizado
- coexistencia controlada entre capa legacy y capa EIL nueva
- seed persistente de dominios públicos en BD
- integración inicial de EIL en pipeline

## Componentes EIL ya introducidos
### Legacy preservado
- `OperatingOrganization`
- `CorporateDomain`
- `Identity`
- `CorporateMembership`
- `MailboxAccount`

### Capa nueva EIL
- `PublicEmailDomain`
- `EmailIdentity`

## Servicios EIL operativos
Ubicación:
- `apps/tenancy/services/domain_resolution.py`

Funciones introducidas/estabilizadas:
- `extract_domain_from_email`
- `is_public_email_domain`
- `resolve_operating_organization_from_domain`
- `resolve_operating_organization_from_email`
- `create_provisional_organization`
- `resolve_email_identity`
- `resolve_organization`

## Integraciones realizadas
### Ingest
- `services/email_ingest.py`
  - asegura contexto EIL
  - resuelve identidad y organización antes de continuar pipeline

### CRM update engine
- `apps/crm_update_engine/entrypoints.py`
  - añade resolución EIL antes de facts/inferences/proposals/recommendations

### SMLL / bootstrap
- `apps/emailing/services/smll_bootstrap.py`
  - mantiene compatibilidad con `MailboxAccount`
  - asegura organización/dominio de simulación

### Provider routing
- `apps/emailing/services/provider_router.py`
  - mantiene `MailboxAccount` como identidad canónica de provider/runtime
  - evita heurística ambigua

## Seed de dominios públicos
Migración añadida:
- `apps/tenancy/migrations/0002_seed_public_email_domains.py`

Dominios seedados:
- gmail.com
- googlemail.com
- outlook.com
- hotmail.com
- live.com
- msn.com
- yahoo.com
- ymail.com
- icloud.com
- me.com
- proton.me
- protonmail.com
- aol.com

## Tests validados
Suites en verde:
- `apps.tenancy.tests_identity`
- `apps.simulated_personas.tests_runtime`
- `apps.emailing.tests_smll_integration`
- `apps.recommendations.tests_execution_engine`

## Conclusión
La fase 1 de EIL queda cerrada a nivel fundacional:
- tenancy coherente
- EIL introducido sin romper legacy
- seed público persistente
- puntos de entrada iniciales integrados
- bloque crítico de tests en verde

## Riesgos pendientes
- `EmailIdentity` aún no es la capa primaria en todo el sistema
- muchos consumers siguen dependiendo de `MailboxAccount`
- aún no se ha refactorizado de forma amplia `apps/emailing/models.py`
- falta extensión de EIL a más puntos inbound/outbound

## Recomendación
La siguiente sesión debe centrarse en:
1. profundización EIL
2. extensión del resolver a más consumers
3. consolidación de persistencia de identidad/organización en el pipeline
4. solo después, continuar con Entity Manager
