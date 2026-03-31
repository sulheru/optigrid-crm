# SESSION LOG — 2026-03-31

## Tema
Identity & Corporation Layer V1 + estabilización tenancy/SMLL/provider layer

## Resumen ejecutivo
Sesión dedicada a cerrar la base fundacional multi-corporation sin introducir sobreingeniería ni romper compatibilidad.

La decisión crítica fue consolidar que:
- `OperatingOrganization` es la corporation canónica
- `MailboxAccount` sigue siendo el buzón canónico

A partir de ahí se estabilizó tenancy y se alineó con SMLL y el provider layer.

## Decisiones tomadas
- NO crear un modelo `Corporation` separado
- NO duplicar `MailboxAccount`
- SÍ extender tenancy con:
  - `CorporateDomain`
  - `Identity`
  - `CorporateMembership`
- NO inferir tenant desde el remitente externo
- SÍ permitir fallback seguro solo cuando haya dirección de mailbox del sistema
- NO implementar envío automático

## Trabajo realizado
- reconstrucción y estabilización real de `apps/tenancy/models.py`
- corrección de imports y compatibilidad interna
- revisión del pipeline de emailing
- revisión del engine SMLL
- revisión de bootstrap y prompt builder
- refuerzo de `provider_router.py`
- alineación del bootstrap con `CorporateDomain`
- corrección del uso de `mailbox_account.email`

## Incidencias durante la sesión
Hubo múltiples iteraciones por:
- modelos tenancy rotos/incompletos
- inconsistencias entre models y migrations
- imports rotos
- intentos fallidos de aliasado conceptual
- nombres de índices/migrations
- referencia a `apps.crm_update_engine.entrypoints` inexistente

Todas esas incidencias quedaron superadas para el scope actual.

## Estado final
- 25 tests OK
- `manage.py check` OK
- tenancy estable
- SMLL estable
- provider layer estable
- pipeline aún degradando limpiamente por falta del entrypoint real del CRM Update Engine

## Deuda técnica identificada
- drift de migraciones en `knowledge`
- migraciones pendientes o ajustes futuros en tenancy según evolución
- falta de entrypoint real para CRM Update Engine
- tenant/mailbox scope aún no persistido canónicamente en emailing

## Recomendación
La próxima sesión debe centrarse solo en cerrar:
- `apps.crm_update_engine.entrypoints.process_email`

sin tocar UI ni providers reales.
