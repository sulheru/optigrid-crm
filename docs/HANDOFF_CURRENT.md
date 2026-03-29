# HANDOFF — CURRENT STATE

## Estado general
El sistema ha quedado operable, observable y correctamente delimitado por tenant antes de entrar en simulación avanzada.

## Capacidades activas

### Action Loop
- Dashboard con recomendaciones reales
- Approval manual desde UI
- Dismiss manual desde UI
- Materialización recommendation → ExternalActionIntent
- Inspección posterior en admin

### External Actions
- Admin alineado con el modelo real
- Lista y detalle funcionales
- payload y normalized_preview visibles
- approval / dispatch / execution visibles
- tenant y mailbox visibles

### Tenancy
- OperatingOrganization define la frontera de memoria
- MailboxAccount representa buzones/actores dentro de esa empresa
- Existe tenant simulado separado para futuras pruebas SMLL

### Scoping básico
- AIRecommendation puede pertenecer a una empresa operadora y a un buzón
- ExternalActionIntent puede pertenecer a una empresa operadora y a un buzón
- Action Loop propaga scoping recommendation → intent

## Estado técnico
- Dashboard carga correctamente
- Outbox carga correctamente
- Admin de intents carga correctamente en lista y detalle
- El sistema está listo para modelar interlocutores simulados persistentes antes de SMLL

## Limitaciones actuales
- El resto del CRM aún no está tenantizado
- El dedupe por tenant en leads/contactos aún no está implementado
- No existe aún SimulatedPersona
- No existe aún SMLL
