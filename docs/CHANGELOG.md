# CHANGELOG

## 2026-03-22 — UI FOUNDATION V2 + label system

### Completado
- Consolidación de `templates/base.html` como app shell compartido
- Sidebar y topbar reutilizables
- Integración de assets en `static/app_ui/`
- Resolución de serving de static files
- Refactor visual completo de:
  - Dashboard
  - Inbox
  - Outbox
- Implementación de un design system ligero:
  - botones
  - badges
  - cards
  - spacing base
- Introducción de capa semántica de labels:
  - `apps/core/labels.py`
  - `apps/core/templatetags/label_filters.py`
- Limpieza de labels técnicas en:
  - dashboard
  - inbox
  - outbox

### Validado
- `label_filters` registrado correctamente en Django template libraries
- Templates cargando sin error
- Static funcionando correctamente
- Navegación principal operativa

### Pendiente
- Refactor de `templates/recommendations/list.html`
- Unificación final de iconografía por tipo
- Limpieza de restos legacy visuales/semánticos
