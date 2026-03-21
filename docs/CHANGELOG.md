# CHANGELOG

## 2026-03-21 — UI FOUNDATION V2 + Cockpit V2B Phase 1

### Completado
- Consolidación de `templates/base.html` como sistema visual común.
- Limpieza y normalización de vistas activas:
  - `templates/dashboard/home.html`
  - `templates/strategy/chat.html`
  - `templates/recommendations/list.html`
  - `templates/tasks/list.html`
  - `templates/emailing/inbox.html`
  - `templates/emailing/outbox.html`
  - `templates/lead_research/list.html`
- Eliminación de estilos inline en vistas activas tratadas.
- Eliminación de redefiniciones peligrosas de clases base (`.page`, `.card`, `.btn`, `.filters`, etc.) en pantallas activas.
- Auditoría y limpieza de templates legacy / backups.
- Eliminación de duplicado peligroso de inbox en `apps/emailing/templates/emailing/inbox.html`.
- Cierre efectivo de UI FOUNDATION V2A.

### Dashboard / Cockpit
- Dashboard evolucionado de vista informativa a cockpit inicial.
- Añadido bloque **AI Recommended Actions** en dashboard.
- Priorización de acciones por `confidence`.
- Introducido mapping semántico de acciones en dashboard:
  - `followup` → `Send Follow-up`
  - `reply_strategy` → `Prepare Reply`
  - `contact_strategy` → `Start Contact`
  - `next_action` / `qualification` → `Create Task`
  - `opportunity_review` → `Promote to Opportunity`
  - `pricing_strategy` / `timing_strategy` → `Review Strategy`
  - `risk_flag` → `Review Risk`
  - `hold` → `No Action`

### Recommendations
- Refactor completo de `apps/recommendations/views.py` restaurando y consolidando:
  - `recommendation_list`
  - `recommendation_create_task`
  - `recommendation_dismiss`
  - `recommendation_promote_opportunity`
  - `execute_followup`
- Refactor de `apps/recommendations/urls.py` con endpoint nuevo:
  - `/recommendations/<id>/execute-followup/`
- `templates/recommendations/list.html` actualizado con botón `Execute` para recomendaciones `followup`.

### Ejecución real
- Primer loop funcional real:
  - Recommendation
  - Execute
  - `execute_followup`
  - generación de draft follow-up
  - redirección a Outbox

### Verificaciones
- `python manage.py check` limpio tras los refactors finales.
- URLs y views críticas verificadas.
- `runserver` final sin error de código; solo puerto ya en uso.

### Pendiente
- Evitar duplicados en `execute_followup`.
- Marcar recommendations ejecutadas (`status=executed`) tras ejecución real.
- Extender Execute real a:
  - `reply_strategy`
  - `contact_strategy`
  - otras acciones operativas.
