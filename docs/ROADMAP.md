# ROADMAP — OptiGrid CRM

## FASE ACTUAL: V3 COMPLETE

✔ Inbox Intelligence V2  
✔ Outbox editable  
✔ Automation Layer V3  
✔ Supervisor UI para Inbox  
✔ Supervisor UI para Tasks  
✔ Inbox filters de supervisor  

---

## FASE 3.5 — UI FOUNDATION V1

### 1. Shared Layout
- `base.html`
- navegación global reutilizable
- estilos comunes mínimos
- estructura shell de aplicación

### 2. Global Navigation
- Dashboard
- Strategic Chat
- Mailing
  - Outbox
  - Inbox
- Recommendations
- Tasks
- Opportunities
- Leads

### 3. Progressive Migration
- migrar primero:
  - Inbox
  - Outbox
  - Tasks
- después:
  - Dashboard
  - Recommendations
  - Opportunities
  - Leads
  - Strategic Chat

---

## FASE 4 — Governance & Control

### 1. Automation Settings en BD
- auto apply enabled
- score threshold
- blocked actions
- blocked risk flags
- fallback a settings.py

### 2. Reversibilidad ampliada
- revocar drafts auto-generados
- revertir cambios de stage
- mayor trazabilidad de acciones automáticas

---

## FASE 5 — Strategic Layer (Jarvis)

### Chat estratégico
- "¿qué oportunidades priorizo?"
- "¿qué leads son más prometedores?"
- "¿qué follow-ups enviar hoy?"
- "¿qué automatizaciones debería ajustar?"

---

## FASE 6 — Communication Layer

- integración Outlook real
- IMAP sync
- envío real emails
- mailbox orchestration

---

## FASE 7 — AI Memory

- vector DB
- contexto histórico
- aprendizaje continuo
- memoria operativa comercial

---

## FASE FINAL

AI Commercial Team semiautónomo y gobernable:

- lead gen
- outreach
- follow-up
- pipeline supervision
- closing support

Usuario = CEO / Supervisor
