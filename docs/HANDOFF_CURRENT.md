# HANDOFF — CURRENT STATE
## OptiGrid CRM — AI Commercial Operating System

### Estado general

El sistema ha completado la consolidación del NBA Engine V1.

Existe ahora una única fuente de verdad para la selección de la acción principal:
- apps/recommendations/nba.py

Se elimina la dualidad conceptual con ranking_engine.

---

### Arquitectura actual validada

Pipeline completo:

Email → Fact → Inference → Recommendation → Task → Opportunity

Capas operativas:

- Communication Layer (Emailing)
- CRM Core (Facts, Inferences, Entities)
- Decision Layer (Recommendations + NBA Engine)
- Execution Layer (Tasks, Opportunities, Drafts)
- UI Cockpit (Dashboard, Inbox, Recommendations, Tasks)

---

### NBA Engine

Estado:

- compute_score → operativo
- get_next_best_action → operativo
- get_next_best_action_explained → operativo
- get_score_breakdown → operativo

Scoring:

- priority_score → runtime
- urgency_score → runtime
- confidence → persistido

No se persisten scores → cálculo dinámico

---

### Tests

- tests_nba → OK
- manage.py check → OK
- sistema estable

---

### Dashboard

- bloque “What should you do now” estable
- una única acción principal
- sin duplicidad de cálculo

---

### Estado conceptual del sistema

El sistema ha evolucionado de:

CRM con recomendaciones

a:

Decision Engine con interfaz (AI-first cockpit)

---

### Próximo salto arquitectónico

External Port System V1 (NO implementado)

- no existe aún:
  - ExternalActionIntent
  - Policy Gate explícito
  - Port Router
  - Adapter Layer formal

pero el sistema está preparado para ello.

---

### Riesgos actuales

- ranking_engine.py aún existe (deuda técnica leve)
- ausencia de contratos formales para integración externa
- ausencia de control explícito de acciones externas

---

### Conclusión

Core estable, coherente y listo para expansión controlada.

Siguiente fase: diseño de puertos (arquitectura, no implementación)
