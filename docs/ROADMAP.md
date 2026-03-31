# ROADMAP — OPTIGRID CRM (IA-FIRST)

## VISIÓN

Construir un CRM IA-first donde:

Signals → Reasoning → Decisions → Actions

El sistema no es una base de datos, es un motor de interpretación y acción.

---

# 🧱 FASE 0 — FOUNDATION (COMPLETADA)

## Objetivo
Pipeline mínimo funcional y estable

## Entregado

- CRM Update Engine V1
  - FactRecord
  - InferenceRecord
  - CRMUpdateProposal
  - AIRecommendation

- Pipeline:
  email → fact → inference → proposal → recommendation

- Idempotencia garantizada
- Tests de integración pasando
- Señales básicas (pricing)

## Estado

🟢 COMPLETADO

---

# ⚙️ FASE 1 — RULE ENGINE (SIGUIENTE)

## Objetivo

Desacoplar lógica de negocio del código

## Entregables

- Estructura RULES declarativa
- Rule evaluator
- Integración con proposals
- Compatibilidad con tests actuales

## Resultado esperado

Signals → Rules → Proposals

## Estado

🟡 INMEDIATO

---

# 🧠 FASE 2 — KNOWLEDGE LAYER

## Objetivo

Persistir conocimiento útil para decisiones

## Entregables

- Knowledge storage (vectorial o estructurado)
- Enriquecimiento de contexto
- Reutilización de patrones

## Ejemplo

"He aprendido a responder pricing → reutilizar estrategia"

## Estado

🟡 CORTO PLAZO

---

# 🤖 FASE 3 — LLM INTEGRATION (SMLL → REAL)

## Objetivo

Introducir razonamiento dinámico

## Entregables

- LLM para:
  - generación de respuestas
  - interpretación avanzada
  - sugerencias

- Integración con:
  - proposals
  - recommendations

## Notas

- Mantener fallback determinista
- No romper pipeline

## Estado

🟡 MEDIO PLAZO

---

# 📬 FASE 4 — MAIL PROVIDERS (REAL WORLD)

## Objetivo

Conectar con el mundo real

## Entregables

- Microsoft 365
- Gmail
- Sync bidireccional

## Estado

🟡 MEDIO PLAZO

---

# 🧩 FASE 5 — UI CONFIGURACIÓN

## Objetivo

Control humano del sistema

## Entregables

- Configuración de:
  - LLM
  - reglas
  - automatizaciones
  - providers

## Estado

🟡 MEDIO PLAZO

---

# 🧠 FASE 6 — AUTONOMOUS LAYER

## Objetivo

Sistema proactivo

## Entregables

- Sugerencias automáticas
- Auto-acciones (con aprobación)
- Aprendizaje continuo

## Ejemplo

"He aprendido X → ¿quieres automatizarlo?"

## Estado

🔵 LARGO PLAZO

---

# 🔐 FASE 7 — SAFETY & CONTROL

## Objetivo

Evitar decisiones irreversibles sin control

## Entregables

- Approval system (ya iniciado)
- Policy engine
- Risk model

## Regla clave

Acciones irreversibles → requieren aprobación

## Estado

🟡 CONTINUO

---

# 🏢 FASE 8 — MULTI-CORPORATION

## Objetivo

Escalar a múltiples empresas

## Entregables

- Identity layer
- Corporate domains
- Context isolation

## Estado

🟡 EN PROGRESO (base ya creada)

---

# 📊 FASE 9 — OBSERVABILITY

## Objetivo

Entender el sistema

## Entregables

- Métricas de pipeline
- Logs estructurados
- Debugging avanzado

## Estado

🟡 FUTURO CERCANO

---

# 🧭 PRINCIPIOS

- IA-first, no CRUD-first
- Determinismo antes que magia
- Automatizar solo lo reversible
- No romper pipeline existente
- Simplicidad > sobreingeniería

---

# 🟢 ESTADO GLOBAL

Foundation sólida completada.

Siguiente paso natural:
👉 RULE ENGINE

