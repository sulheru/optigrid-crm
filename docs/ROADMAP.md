# ROADMAP

## Estado actual
Base fundacional de tenancy/corporation consolidada y estable.

## Decisiones ya cerradas
- `OperatingOrganization` es la corporation canónica del sistema.
- `MailboxAccount` sigue siendo la entidad canónica de buzón.
- Se añade capa fundacional de tenancy con:
  - `CorporateDomain`
  - `Identity`
  - `CorporateMembership`
- La resolución por dominio existe en:
  - `apps.tenancy.services.domain_resolution`
- El provider layer SMLL mantiene control estricto:
  - requiere `mailbox_account` explícito
  - o una dirección de mailbox del sistema resoluble de forma segura
- No se infiere tenant desde el remitente externo del cliente.
- No se implementa envío automático de emails bajo ninguna circunstancia.

## Lo completado en esta sesión
- estabilización completa de `apps/tenancy/models.py`
- coherencia entre tenancy y SMLL
- corrección del `prompt_builder` para usar el campo real `mailbox_account.email`
- alineación del bootstrap SMLL con `CorporateDomain`
- refuerzo del provider layer con resolución segura de mailbox
- validación completa:
  - tests verdes
  - `manage.py check` limpio

## Próximos pasos recomendados
1. Implementar `apps.crm_update_engine.entrypoints.process_email`
2. Conectar ese entrypoint con el pipeline actual
3. Persistir tenant scope/mailbox scope en entidades de emailing
4. Reducir dependencia de `mailbox_account` inyectado externamente
5. Preparar futura integración con providers reales sin romper SMLL

## Fuera de alcance inmediato
- UI de tenancy / identity
- login corporativo real
- providers M365/Gmail reales
- autoenvío
- refactor masivo de emailing
