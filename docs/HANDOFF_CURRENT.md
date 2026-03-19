# HANDOFF — CURRENT STATE

---

## 🧠 CONTEXTO GENERAL

Proyecto:

OptiGrid CRM → evolucionando a AI Commercial Operating System

Objetivo:

Construir un sistema donde la IA ejecuta funciones comerciales completas y el usuario actúa como supervisor.

---

## ✅ ESTADO ACTUAL

### CORE

- Pipeline completo operativo:
  Email → Fact → Inference → Proposal → Recommendation → Task → Opportunity

- UI funcional:
  - oportunidades
  - tareas
  - recomendaciones

---

### OPPORTUNITY INTELLIGENCE V2

- scoring
- priority
- risk flags
- next actions
- análisis batch
- reuse de recommendations/tasks

Comando:
python manage.py analyze_open_opportunities

---

### AUTOTASKER

- generación automática de tareas
- integración con recommendations

---

### GOVERNANCE BASE

- tasks pueden ser revocadas
- persistencia de decisiones humanas
- sistema respeta `is_revoked`

---

### STRATEGY LAYER

Estado:

- Strategy Chat V1 funcional
- Strategy Chat V2 iniciado

Fix aplicado:

- eliminación de referencia a `StrategyChatView` inexistente
- sistema estable (`python manage.py check` OK)

---

## ⚠️ LIMITACIONES ACTUALES

- No hay discovery autónomo de empresas
- No hay enrichment estructurado
- No hay hipótesis comerciales automáticas
- No hay outbound automatizado
- Jarvis no ejecuta acciones aún

---

## 🎯 SIGUIENTE OBJETIVO

FASE 4 — Target Intelligence Layer

---

## 🧩 BLOQUES A IMPLEMENTAR

1. LeadSuggestion model
2. LeadSignal model
3. LeadResearchSnapshot
4. Signal Discovery Engine (Gemini)
5. Memory / dedupe system
6. Celery task
7. Inbox UI

---

## 🔁 FLUJO OBJETIVO INMEDIATO

Gemini → discovery → dedupe → store → inbox → approve → CRM

---

## 🧠 PRINCIPIO CLAVE

El sistema debe pasar de:

- reaccionar a emails

A:

- generar oportunidades activamente

---

## 📍 SIGUIENTE SESIÓN

Arrancar:

apps/lead_research/

---

