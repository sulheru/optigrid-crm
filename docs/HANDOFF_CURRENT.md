# HANDOFF CURRENT

## Proyecto
OptiGrid CRM

## Fecha de cierre
2026-04-03

## Fase actual
Inbox Decision Integration Cleanup cerrado a nivel de inbox y validación runtime básica.

## Estado real alcanzado

### Cerrado y estable
- Inbox renderiza correctamente con `inbox_decision_panel`.
- La integración view/template quedó funcional.
- Se corrigieron varios problemas de wiring en `apps/emailing/views.py`.
- Se restauraron views de outbox/inbox que se habían roto durante refactors intermedios.
- `inbox_email_card.html` quedó alineado con tests en el label **"View decision"**.
- El script de fetch fue corregido para usar únicamente rutas existentes:
  - válido: `/inbox/<id>/decision/`
  - inválido: `/inbox/<id>/`

### Estado visual validado
- Las páginas `/inbox/<id>/decision/` cargan correctamente.
- Se muestra la decisión operativa persistida:
  - action_type
  - status
  - priority
  - score
  - requires approval
  - automatic
  - automation reason
  - risk flags
- Cuando no hay trace enriquecido, la UI ya no dice falsamente "Decision Not Available" mientras sí muestra una decisión.
- En su lugar muestra el estado correcto:
  - **Trace Not Available**

## Problema pendiente principal
La resolución de `decision_output` / `trace` en `apps/emailing/decision_detail.py` sigue incompleta para datos reales.

## Síntoma pendiente
En múltiples casos reales, la página muestra:
- decisión operativa persistida disponible
- semantic effect ausente
- selected/discarded rules ausentes
- explanation ausente
- banner `Trace Not Available`

Esto indica que:
- existe `InboundDecision`
- pero no se está resolviendo correctamente el trace o `decision_output`
- o no existe en la forma que la vista espera

## Diagnóstico más probable
El bug pendiente está en uno o varios de estos puntos:
1. nombre real del campo o relación usado para `InboundDecision`
2. recuperación de `RuleEvaluationLog`
3. estructura real de `payload_json`
4. diferencia entre el formato de persistencia real y el que esperan los tests

## Decisión arquitectónica tomada
No crear `/inbox/<id>/` como vista nueva para esta fase.

Motivo:
- el problema estaba en el script, no en el routing
- la ruta necesaria para esta fase es `/inbox/<id>/decision/`

## Ficheros tocados en la sesión
- `apps/emailing/views.py`
- `templates/emailing/inbox.html`
- `templates/emailing/partials/inbox_email_card.html`
- `templates/emailing/partials/inbox_decision_panel.html`
- `apps/emailing/decision_detail.py`
- `templates/emailing/decision_detail.html`
- `tmp/fetch_decisions.sh`

## Resultado neto de la sesión
La fase "Inbox Decision Integration Cleanup" queda cerrada desde el punto de vista de:
- inbox
- panel de decisión en inbox
- consistencia básica UI
- script de validación

La fase que queda abierta ya no es inbox, sino:
- **Decision Detail trace recovery**

## Siguiente foco recomendado
Resolver correctamente `decision_output` y `trace` para que `Decision Detail` pueda mostrar:
- Selected Rules
- Discarded Rules
- Explanation
- Semantic Effect
cuando esos datos existan realmente.

