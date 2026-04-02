# ROADMAP — OptiGrid CRM (IA-First Decision System)

## Estado actual

El sistema dispone de un motor de decisión completamente estructurado:

V2.0 → Rule Engine (desacople lógica)
V2.1 → Declarative Conditions
V2.2 → Trace Semantics
V2.3 → Structured Trace Model
V2.4 → Query Layer (helpers)
V2.5 → Explainability Layer
V2.6 → Decision Output Layer

Estado: ✅ CORE DECISION SYSTEM COMPLETO

---

## Fase actual

### V2.7 — Decision UI Integration (INMEDIATO)

Objetivo:
Exponer decisiones en UI / Chat Console.

Incluye:
- get_email_decision_view(email_id)
- consumo de build_decision_output
- render de:
  - selected_rules
  - discarded_rules
  - explanation
  - final_effect

Resultado esperado:
- debugging humano viable
- validación de decisiones
- transparencia operativa

---

## Próxima fase

### V2.8 — Interactive Decision UI

Objetivo:
Hacer la decisión navegable y explorable.

Incluye:
- click en regla → detalle
- mostrar condiciones evaluadas
- mostrar discard_reason
- highlight de regla final
- agrupación por tipo de descarte

Resultado:
- UI explicativa real
- herramienta de análisis

---

### V2.9 — Decision Persistence (Audit Layer)

Objetivo:
Persistir decisiones para auditoría.

Incluye:
- modelo DecisionSnapshot
- almacenamiento de:
  - trace
  - decision_output
- versionado de decisiones

Resultado:
- auditoría histórica
- reproducibilidad

---

### V3.0 — Feedback Loop (Human-in-the-loop)

Objetivo:
Permitir corrección humana de decisiones.

Incluye:
- override manual
- marcar decisión correcta/incorrecta
- feedback estructurado

Resultado:
- base para aprendizaje futuro
- mejora continua

---

### V3.1 — Adaptive Rule System

Objetivo:
Sistema semi-dinámico de reglas.

Incluye:
- reglas parametrizables
- activación/desactivación
- priorización configurable

Resultado:
- flexibilidad sin romper determinismo

---

### V3.2 — AI-Augmented Decisions (SAFE MODE)

Objetivo:
Introducir IA sin perder control.

Incluye:
- sugerencias IA (NO ejecución)
- comparación:
  - decisión rule-based
  - sugerencia IA
- flag de divergencia

Resultado:
- validación antes de automatización

---

### V3.3 — Auto-Optimization Layer

Objetivo:
Que el sistema proponga mejoras.

Incluye:
- detección de patrones
- sugerencias tipo:
  "He aprendido a hacer X, ¿activar?"

Resultado:
- sistema evolutivo

---

## Principios del roadmap

1. Determinismo primero
2. Explicabilidad antes que automatización
3. UI como herramienta de validación
4. IA como asistente, no decisor inicial
5. Separación estricta de capas

---

## Estado global

CORE ENGINE: ✅
TRACEABILITY: ✅
EXPLAINABILITY: ✅
OUTPUT: ✅
UI: ⏳ (V2.7)
INTELLIGENCE LOOP: 🔜

