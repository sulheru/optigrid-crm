# ROADMAP — OPTIGRID CRM

---

## FASE ACTUAL

### ✅ COMPLETADO

#### 1. Core Pipeline
Email → Fact → Inference → Recommendation → Task → Opportunity

#### 2. Execution Layer
- ejecución unificada
- drafts funcionales
- integración con recommendations

#### 3. Provider Abstraction
- LLM desacoplado
- runtime configurable

#### 4. Governance Layer V1
- control estructural básico

#### 5. Recommendation Merge Layer V1
- unificación rules + LLM
- deduplicación
- source tracking
- persistencia coherente

---

## 🔄 EN PROGRESO

### 6. Cockpit V3 — Next Best Action Engine

Objetivo:
→ convertir el sistema en decisor operativo

Incluye:

- ranking global
- urgency system
- type weighting
- selección de 1 acción

Estado actual:
PARCIALMENTE IMPLEMENTADO Y ESTABLE

Ya realizado:
- `apps/recommendations/nba.py`
- scoring runtime no persistido
- reglas de urgencia V1
- tests base OK
- bloque dashboard operativo

Pendiente:
- consolidar un único motor NBA canónico
- eliminar dualidad conceptual con `ranking_engine`
- conectar dashboard al camino definitivo sin duplicidad

---

## 🔜 SIGUIENTE

### 7. NBA Consolidation / Dashboard Canonicalization

- unificar `nba.py` y `ranking_engine.py`
- definir motor canónico único
- usar una sola ruta para `best_action`
- mantener compatibilidad visual y funcional
- validar fallback cuando no haya recommendations válidas

---

## 🔮 FUTURO

### 8. Dashboard Intelligence V2
- explainability ligera
- alternatives panel más claro
- score visible y consistente

### 9. Merge Layer V2
- explainability
- scoring avanzado
- conflict resolution

### 10. Governance V2
- políticas dinámicas
- validación avanzada

### 11. Autonomy Layer
- ejecución semi-automática
- loops controlados
- feedback system

### 12. Learning Layer
- ajuste de scoring
- optimización basada en resultados

---

## VISIÓN FINAL

Sistema IA-first que:

- decide qué hacer
- prioriza automáticamente
- ejecuta con supervisión humana
