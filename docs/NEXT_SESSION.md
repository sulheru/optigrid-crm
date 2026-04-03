# NEXT SESSION

## Objetivo
Cerrar el primer bloque crítico del core operativo real:
**canonical mailbox identity + execution boundary audit**

## Preguntas que debe responder la sesión
1. ¿Dónde debe vivir la identidad operativa canónica de mailbox?
2. ¿Qué entidades deben persistir:
   - operating organization
   - mailbox account
   - provider
   - tenant scope
3. ¿Qué hueco exacto existe entre:
   - decisión
   - recomendación
   - acción ejecutable
4. ¿Cómo debe verse la primera versión mínima del execution engine?

## Capas a inspeccionar
- tenancy / mailbox identity
- emailing input / routing
- execution / application
- recommendations / action materialization
- provider runtime

## Ficheros prioritarios para inspección
- `apps/tenancy/models.py`
- `apps/tenancy/services/domain_resolution.py`
- `apps/emailing/models.py`
- `apps/emailing/services/provider_router.py`
- `apps/emailing/services/mail_provider_service.py`
- `apps/emailing/services/outbound_sender.py`
- `apps/emailing/services/inbound_decision_apply_service.py`
- `apps/recommendations/models.py`
- `apps/recommendations/execution_application.py`
- `apps/recommendations/execution.py`
- `apps/providers/mail_provider.py`
- `apps/providers/mail_runtime.py`
- `apps/providers/mail_registry_v2.py`

## Entregables esperados
1. mapa del modelo canónico de mailbox/account/provider
2. diagnóstico exacto del hueco decisión → ejecución
3. definición del mínimo execution engine necesario
4. orden realista de cierre del core operativo

## No hacer
- no empezar aún el sistema de plugins
- no refactorizar aún el sidebar a navegación dinámica
- no implementar aún manifests
- no introducir aún uninstall/install de plugins

## Criterio de éxito
Terminar la sesión con una definición clara, basada en código real, de:
- identidad operativa canónica
- frontera decisión → ejecución
- mínimo núcleo restante para declarar el core listo para producción
