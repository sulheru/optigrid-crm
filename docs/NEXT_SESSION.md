# NEXT SESSION

## CONTEXTO

Merge Layer V1 completada.
NBA Engine V1 ya está creado y estable.
Dashboard vuelve a cargar.
Tests y system check OK.

Sin embargo, se ha detectado dualidad entre:

- `apps/recommendations/nba.py`
- `apps/recommendations/ranking_engine.py`

---

## OBJETIVO

COCKPIT V3 — NBA ENGINE CONSOLIDATION

Cerrar la implementación del Next Best Action Engine
dejando un único motor canónico de priorización.

---

## TAREA PRINCIPAL

### 1. Consolidación NBA

Revisar:

- `apps/recommendations/nba.py`
- `apps/recommendations/ranking_engine.py`
- `apps/dashboard_views.py`

Objetivo:
- decidir cuál será el motor canónico
- evitar coexistencia redundante
- mantener compatibilidad con dashboard actual

---

## IMPLEMENTACIÓN ESPERADA

### A. Canonical Path
Definir una única función fuente de verdad para:

- seleccionar best action
- calcular scoring final
- exponer recommendation principal al dashboard

### B. Dashboard
Asegurar que:

- `best_action` sale del motor canónico
- no haya doble cálculo conceptual
- el bloque "What should you do now" use el resultado correcto

### C. Validación
Ejecutar:

- `python3 manage.py check`
- tests relevantes
- validación visual dashboard

---

## REGLAS

- no tocar execution layer
- no persistir score
- no añadir complejidad nueva
- no mantener dos motores paralelos sin necesidad
- validar contexto real antes de tocar código
- entregar cambios con ficheros completos

---

## CRITERIO DE ÉXITO

- un solo motor NBA canónico
- dashboard estable
- una única acción principal clara
- sin duplicidad conceptual
- base lista para evolución futura
