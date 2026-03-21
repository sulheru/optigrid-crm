# CHANGELOG — OptiGrid CRM

## UI FOUNDATION V1 (2026-03-21)

### Added
- base.html como layout global de la aplicación
- partial reutilizable: partials/app_nav.html
- navegación global consistente (sidebar)

### Updated
- Inbox → migrado a base.html
- Outbox → migrado a base.html
- Tasks → migrado a base.html
- Recommendations → migrado correctamente (fix en views.py)
- Strategic Chat → migrado a base.html
- Dashboard → adaptado a layout común
- Leads → adaptado a layout común

### Fixed
- navegación duplicada en múltiples templates
- uso incorrecto de templates legacy en recommendations
- desaparición del sidebar en Strategic Chat
- desalineación visual en Tasks (body padding conflict)
- inconsistencias de variables en filtros (status / type)

### Refactor
- eliminación de templates standalone con `<html>` / `<body>`
- normalización de `.page` y `.page-header`
- limpieza de CSS redundante

### Notes
- el sistema ahora funciona como una aplicación unificada (no pantallas aisladas)
- base sólida para dashboard real, settings y strategy layer

