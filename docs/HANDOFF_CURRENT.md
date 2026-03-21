# HANDOFF CURRENT

## Estado general
OptiGrid CRM ha pasado de UI funcional dispersa a cockpit unificado con primeras acciones operativas reales.

## Punto exacto del proyecto
### Completado
- UI FOUNDATION V2A cerrada.
- Dashboard con bloque `AI Recommended Actions`.
- Mapping semántico en dashboard para recomendaciones.
- Recommendations app refactorizada y estable.
- Execute real implementado para recomendaciones tipo `followup`.

### Estado técnico estable
- `python manage.py check` limpio en validación final.
- URLs críticas de recommendations definidas.
- Template `recommendations/list.html` con botón `Execute`.
- `dashboard_views.py` usando `top_actions`.

---

## Ficheros clave tocados en esta sesión
- `templates/base.html`
- `templates/dashboard/home.html`
- `templates/strategy/chat.html`
- `templates/recommendations/list.html`
- `templates/tasks/list.html`
- `templates/emailing/inbox.html`
- `templates/emailing/outbox.html`
- `templates/lead_research/list.html`
- `apps/dashboard_views.py`
- `apps/recommendations/views.py`
- `apps/recommendations/urls.py`

---

## Estado funcional actual
### Dashboard
- Muestra métricas
- Muestra AI Recommended Actions
- Expone Execute / Inspect / Dismiss en cockpit

### Recommendations
- Lista operativa
- Execute disponible para `followup`
- create-task / dismiss / promote-opportunity disponibles

### Outbox
- Recibe drafts derivados del flujo de execute followup

---

## Qué NO tocar a ciegas
- `apps/recommendations/views.py`
- `apps/recommendations/urls.py`
- `templates/dashboard/home.html`

Cualquier cambio aquí debe hacerse con refactor completo, no con reemplazos parciales improvisados.

---

## Riesgos actuales
1. `execute_followup` puede crear duplicados si se pulsa varias veces.
2. No se está marcando la recommendation como `executed`.
3. El mapping semántico ya existe en dashboard, pero no todos los recommendation types tienen ejecución real.
4. Dashboard ya es cockpit inicial, pero aún no muestra urgency ni activity feed.

---

## Recomendación para la próxima sesión
Ir a fiabilidad operativa, no a estética:
1. deduplicación de followup drafts
2. executed state
3. execute real para más recommendation types
4. luego cockpit refinement visual/funcional

---

## Principio activo
NO hacer suposiciones.
Validar contexto antes de implementar.
Trabajar con outputs a `tmp/` para inspección y checks.
