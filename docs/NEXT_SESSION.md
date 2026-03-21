# NEXT SESSION

## Objetivo recomendado
Pasar de **Execute V1** a **Execute fiable y escalable**.

## Prioridad 1 — Robustez operativa
### 1. Evitar duplicados en execute_followup
Antes de crear un nuevo draft follow-up:
- comprobar si ya existe draft follow-up abierto para la misma oportunidad
- si existe, reutilizarlo o redirigir a Outbox sin crear otro

### 2. Marcar recommendation como executed
Cuando `execute_followup` cree o reutilice draft:
- actualizar recommendation status a `executed` si procede
- evitar que siga apareciendo como acción pendiente

---

## Prioridad 2 — Extender Execute real
Añadir ejecución real para:
- `reply_strategy`
- `contact_strategy`
- `next_action`
- `risk_flag` (al menos como task/alerta)
- `pricing_strategy` / `timing_strategy` (task estructurada)

---

## Prioridad 3 — Cockpit V2B phase 2
Una vez estabilizado Execute:
- urgency panel
- activity feed
- quick actions globales
- strategic chat más accionable

---

## Contexto importante
### Ya hecho
- UI FOUNDATION V2A cerrada
- Dashboard con `AI Recommended Actions`
- mapping semántico por `recommendation_type`
- recommendations app estable
- execute_followup funcional

### No rehacer
No repetir limpieza general de UI.
La fase siguiente es de fiabilidad y capacidad operativa.

---

## Ficheros que probablemente habrá que inspeccionar primero
Volcar a `tmp/` antes de tocar nada:
- `apps/recommendations/views.py`
- `apps/recommendations/models.py`
- `apps/emailing/models.py`
- `apps/emailing/views.py`
- `templates/dashboard/home.html`
- `templates/recommendations/list.html`

---

## Meta de la próxima sesión
Conseguir esto:

Recommendation (followup)
→ Execute
→ no duplicar draft
→ marcar executed
→ mostrar estado coherente en dashboard y recommendations

Eso dejará el primer loop operativo realmente fiable.
