# HANDOFF CURRENT

## Fecha
2026-03-31

## Estado funcional
La capa fundacional de corporation/tenancy está estable y validada.

## Decisión arquitectónica clave
- `OperatingOrganization = Corporation`
- No se introduce un modelo `Corporation` separado.
- `MailboxAccount` no se duplica ni se reemplaza.

## Estado de tenancy
Modelos activos y estables:
- `OperatingOrganization`
- `CorporateDomain`
- `Identity`
- `CorporateMembership`
- `MailboxAccount`

## Estado de resolución por dominio
Existe y funciona en:
- `apps.tenancy.services.domain_resolution`

Regla actual:
- se puede resolver organización a partir de dominio
- pero el provider layer no debe inferir tenant a partir del remitente externo del inbound

## Estado de SMLL
- SMLL sigue funcionando
- Tests de SMLL verdes
- `prompt_builder` ya usa el campo real `mailbox_account.email`
- `smll_bootstrap` ya asegura `simulation.local` como dominio de la simulation lab

## Estado de provider layer
Archivo clave:
- `apps/emailing/services/provider_router.py`

Situación actual:
- acepta `mailbox_account` explícito
- tiene fallback seguro usando dirección de mailbox del sistema
- no usa heurísticas ambiguas con el remitente externo

## Estado del pipeline
`apps/emailing/services/email_processing_patch.py` sigue intentando llamar a:
- `from apps.crm_update_engine.entrypoints import process_email`

Pero ese módulo/entrypoint real aún no existe en la ruta esperada.

Esto no rompe tests actuales porque el pipeline degrada con:
- `[SMLL] CRM Update Engine no disponible, pipeline detenido aquí`

## Riesgos controlados
- no autoenvío
- no providers reales
- no acoplamiento fuerte con M365 todavía
- no inferencia insegura de tenant

## Siguiente paso recomendado
Implementar un entrypoint mínimo y canónico:
- `apps/crm_update_engine/entrypoints.py`
- función `process_email(email)`

Objetivo:
- cerrar el loop del pipeline sin tocar UI ni providers reales

## No hacer en la siguiente sesión
- no meter UI
- no meter login real
- no reabrir el debate `OperatingOrganization` vs `Corporation`
- no tocar envío real de correo
