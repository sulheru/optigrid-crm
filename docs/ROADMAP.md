# ROADMAP

## Estado actual
### Fase completada
- Rule Engine determinista
- RULE_TRACE estructurado
- Explainability layer
- Decision Output layer
- Persistencia de trace y decisión operativa
- Decision Detail View funcional a nivel base
- Inbox Decision Panel integrado
- Inbox Decision Integration Cleanup cerrado

### Fase parcialmente completada
- Decision Detail enriched recovery
  - decisión operativa: sí
  - trace/output enriquecido: parcial / pendiente

---

## Próxima fase inmediata
### Decision Detail Trace Recovery
Objetivo:
- resolver correctamente `decision_output` y `trace`

Entregables:
- `Selected Rules`
- `Discarded Rules`
- `Explanation`
- `Semantic Effect`
cuando existan realmente

Criterio de cierre:
- `apps.emailing.test_decision_detail` en verde
- al menos un caso real renderiza salida enriquecida

---

## Siguiente fase después
### Decision → Action UI
Sin implementar aún.

Objetivo:
- exponer apply / dismiss / estado de ejecución de forma limpia

Posibles elementos:
- estado visible de sugerida / aplicada / descartada
- feedback inmediato en inbox
- coherencia entre inbox y detail

---

## Fase posterior
### Decision Execution Boundary
Objetivo:
- formalizar la frontera entre:
  - decision engine
  - approval layer
  - execution layer

Esto debe permitir:
- ejecutar decisiones de forma controlada
- mantener trazabilidad
- evitar side effects ambiguos

---

## Fase posterior
### UI coherence & navigation cleanup
Objetivo:
- homogeneizar navegación entre:
  - inbox
  - decision detail
  - outbox
  - recommendations/tasks/opportunities

---

## Nota estratégica
La prioridad inmediata ya no es inbox.
La prioridad inmediata es:
- **hacer fiable la reconstrucción del detalle de decisión**
