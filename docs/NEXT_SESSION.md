# NEXT_SESSION

## Objetivo
Cockpit V2C — Observabilidad y Prioridad

## Contexto de partida
El backend ya tiene execute unificado operativo y validado para:
- followup
- contact_strategy
- reply_strategy

El siguiente trabajo debe centrarse en cockpit, no en lógica core adicional.

## Prioridad 1 — Dashboard sin mapping manual
Analizar y modificar:
- `apps/dashboard_views.py`
- `templates/dashboard/home.html`

Objetivo:
- eliminar lógica manual de `primary_action_url`
- usar únicamente:
  `/recommendations/<id>/execute/`

## Prioridad 2 — Urgency Panel
Fuentes:
- `InboundInterpretation.urgency`
- `AIRecommendation.status = new`
- `AIRecommendation.confidence`

Salida esperada:
- bloque visible en dashboard
- agrupación high / medium / low
- CTA claros hacia execute o inspect

## Prioridad 3 — Activity Feed
Diseñar e implementar un modelo mínimo tipo:
- `ActivityEvent`
  - `event_type`
  - `aggregate_type`
  - `aggregate_id`
  - `summary`
  - `payload_json`
  - `triggered_by_type`
  - `triggered_by_id`
  - `created_at`

Primeros eventos a registrar:
- `recommendation_executed`
- `outbound_draft_created`
- `outbound_draft_reused`
- `task_created_from_recommendation`
- `opportunity_promoted_from_recommendation`

Mostrar últimos eventos en dashboard.

## Regla de trabajo
- no hacer suposiciones
- inspección antes de tocar código
- outputs en `tmp/`
- siempre usar:
  `&> tmp/archivo.txt`
  y después:
  `cat tmp/archivo.txt`
