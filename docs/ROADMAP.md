# ROADMAP

## Fase actual
Cockpit V2C — Observabilidad y Prioridad

## Completado

### UI Foundation V2A
- base.html consolidado
- vistas normalizadas
- sistema visual consistente

### Cockpit V2B — base
- Dashboard con "AI Recommended Actions"
- priorización por confidence
- botón unificado a nivel conceptual

### Execute Reliability
- `followup` ejecutable
- deduplicación funcional
- reuse de drafts
- estado `executed`

### Execute Extensions
- `contact_strategy` ejecutable
- `reply_strategy` ejecutable

### Execute Unificado
- endpoint único `/recommendations/<id>/execute/`
- routing por `recommendation_type`

## En curso / siguiente
### Cockpit V2C
1. Dashboard desacoplado del mapping manual
2. Urgency panel
3. Activity feed
4. Preparación para auto-execute y Strategic Chat

## Posterior
### Extensiones de ejecución
- `next_action`
- `risk_flag`
- `pricing_strategy`
- `timing_strategy`

### Governance avanzada
- políticas de auto-apply
- thresholds por confidence / urgency / risk

### Strategic Chat
- integración directa con execute unificado
- acciones desde consola estratégica
