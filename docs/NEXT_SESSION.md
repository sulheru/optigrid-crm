# NEXT_SESSION — OptiGrid CRM
Sesión siguiente recomendada: EIL Integration Deepening (Phase 2)

## Objetivo
Extender EIL más allá de tenancy e ingest inicial, para que la resolución canónica de identidad y organización impregne más partes del pipeline sin romper compatibilidad con legacy.

## Punto de partida
Ya está hecho:
- `OperatingOrganization`, `CorporateDomain`, `Identity`, `CorporateMembership`, `MailboxAccount`
- `PublicEmailDomain`, `EmailIdentity`
- `domain_resolution.py`
- seed de dominios públicos
- integración inicial en:
  - `services/email_ingest.py`
  - `apps/crm_update_engine/entrypoints.py`

Todo el bloque crítico de tests ejecutado en esta sesión quedó en verde.

## Objetivos concretos de la siguiente sesión
### 1. Ampliar integración EIL
Revisar e integrar EIL en:
- `apps/emailing/models.py`
- `apps/emailing/services/mail_provider_service.py`
- `apps/providers/mail_runtime.py`
- `apps/emailing/services/provider_router.py` si requiere ajuste adicional
- posibles puntos de persistencia inbound/outbound

### 2. Persistencia más explícita
Evaluar si ciertos modelos de correo deben guardar:
- `operating_organization`
- `mailbox_account`
- referencia indirecta o derivable a `EmailIdentity`

### 3. Mantener compatibilidad
No eliminar todavía:
- `MailboxAccount`
- `CorporateDomain`
- `Identity`

Se mantiene estrategia de coexistencia controlada.

### 4. Cerrar criterio arquitectónico
Definir con claridad:
- qué capa es canónica para provider/runtime
- qué capa es canónica para resolución EIL
- cuándo y cómo converger en fases posteriores

## Restricciones
- no login
- no permisos
- no UI
- no providers externos nuevos
- no sustitución masiva de legacy por búsqueda y reemplazo global
- no romper SMLL ni execution engine

## Criterio de éxito
Al terminar la siguiente sesión:
- más puntos del pipeline usarán resolución EIL
- el sistema seguirá en verde
- quedará más claro el camino hacia Entity Manager

## Orden recomendado
1. briefing rápido
2. inspección de ficheros críticos
3. refactorización controlada
4. tests
5. debriefing
6. continuidad
