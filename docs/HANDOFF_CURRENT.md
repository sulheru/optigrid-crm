# HANDOFF_CURRENT

## Proyecto
OptiGrid CRM — AI Commercial Operating System

## Estado operativo actual
El sistema ya dispone de una capa de ejecución funcional sobre recommendations.

### Ejecutables reales confirmados
- `followup`
- `contact_strategy`
- `reply_strategy`

### Endpoint unificado
Existe y funciona:

`/recommendations/<id>/execute/`

Su responsabilidad actual es delegar según `recommendation_type`.

## Lo importante que queda estable
- `AIRecommendation.status` incluye y usa `executed`
- `execute_followup` evita re-ejecuciones y reutiliza drafts
- `contact_strategy` crea o reutiliza `first_contact`
- `reply_strategy` crea o reutiliza `followup`
- la segunda ejecución no genera duplicados en los flujos ya validados

## Decisiones tomadas en esta sesión
1. No forzar todavía una trazabilidad completa multi-origen sobre `OutboundEmail.source_recommendation`.
2. Mantener `source_recommendation` en modelo, pero no basar toda la lógica en ese campo.
3. Priorizar estabilidad operativa e idempotencia antes que una capa completa de event sourcing.
4. Pasar el siguiente foco al cockpit:
   - quitar mapping manual del dashboard
   - usar execute unificado como source of truth
   - añadir urgency panel
   - añadir activity feed

## Riesgos / cautelas
- No sobrescribir `apps/recommendations/views.py` sin inspeccionar primero el fichero completo.
- En sesiones futuras, cualquier output de verificación debe ir a:
  `~/OptiGrid_Project/og_pilot/optigrid_crm/tmp/`
  y mostrarse con `cat` inmediatamente después.
- El dashboard actual aún no está totalmente desacoplado del mapping manual.

## Siguiente foco recomendado
Cockpit V2C:
1. simplificar dashboard para usar solo `/recommendations/<id>/execute/`
2. urgency panel basado en `InboundInterpretation.urgency` + recommendations nuevas
3. modelo mínimo `ActivityEvent`
4. activity feed visible en dashboard
