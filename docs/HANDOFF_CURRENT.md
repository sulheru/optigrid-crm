# HANDOFF CURRENT

## Estado actual
OptiGrid CRM ya tiene una capa visual V2 funcional y coherente para las vistas principales de operación.

## Vistas estabilizadas
- Dashboard
- Inbox
- Outbox

## Base visual
- `templates/base.html` actúa como shell compartido
- Sidebar y topbar ya consolidados
- Design system ligero aplicado sobre el shell
- Assets servidos desde `static/app_ui/`

## Capa semántica
Se ha introducido una capa de labels desacoplada del backend:

- `apps/core/labels.py`
- `apps/core/templatetags/label_filters.py`

Esto evita exponer directamente strings internos como:
- `followup`
- `reply_strategy`
- `contact_strategy`
- `advance_opportunity`

## Punto técnico importante
`label_filters` ya está reconocido por Django. La librería aparece registrada en template libraries, por lo que el problema de carga de filtros quedó resuelto.

## Deuda principal restante
La sección con más deuda ahora mismo es:
- `templates/recommendations/list.html`

Ahí todavía quedan:
- lógica visual hardcodeada
- labels internas
- estilo no totalmente alineado con V2

## Recomendación para siguiente sesión
Entrar directamente a:
1. inspección de `templates/recommendations/list.html`
2. refactor visual completo
3. integración con `label_filters`
4. opcional: iconografía y colores por tipo
