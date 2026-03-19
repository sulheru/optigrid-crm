# ROADMAP — OptiGrid AI Commercial Operating System

## Visión

Construir un sistema donde:

- La IA ejecuta funciones comerciales completas
- El usuario actúa como CEO/supervisor
- El sistema gestiona comunicación, oportunidades y acciones
- El email (Outlook) es backend, no interfaz
- La base de datos está diseñada para IA, no para humanos

---

## Principio clave

IA propone → Humano decide → Sistema ejecuta

---

## Arquitectura objetivo

### Capa 1 — Communication Layer
- Outlook (Microsoft Graph)
- Email ingestion
- Drafts / Send / Threads

### Capa 2 — Operational CRM Core
- Opportunities
- Tasks
- Recommendations
- First Contact System
- Execution State

### Capa 3 — Semantic Engine (Gemini)
- Fact extraction
- Inference
- Draft generation
- Context understanding
- Memory writing

### Capa 4 — Governance Layer
- Auto-task policies
- Auto-reply policies
- Limits (daily send, generation)
- Revocation / lock / override
- Audit trail

### Capa 5 — Strategic Chat (Jarvis)
- Query system state
- Discuss strategy
- Generate actions
- Guide execution

---

## Fases de desarrollo

---

# FASE 1 — GOVERNANCE BASE (CRÍTICO)

Objetivo:
Controlar ejecución automática antes de escalar.

### Implementar:
- Campo en CRMTask:
  - is_revoked (bool)
- Endpoint:
  - revoke task
- UI:
  - botón revoke en tasks
- Autotasker:
  - NO recrear task si:
    - misma opportunity
    - mismo source_action
    - task revocada

### Resultado:
Sistema autónomo controlado.

---

# FASE 2 — OUTLOOK INTEGRATION (INPUT REAL)

Objetivo:
Conectar sistema al mundo real.

### Implementar:

## Autenticación
- OAuth con Microsoft Graph
- almacenamiento de tokens

## Sync
- Inbox
- Sent

## Modelo Email
- subject
- body
- sender
- recipients
- thread_id
- received_at

## Pipeline trigger
Email → Fact → Inference → Recommendation → Task → Opportunity

### Resultado:
Sistema se alimenta automáticamente de emails reales.

---

# FASE 3 — EMAIL THREADING + UI

Objetivo:
Visualizar conversaciones correctamente.

### Implementar:
- agrupación por thread_id
- vista tipo conversación
- timeline
- enlace email → opportunity

### Resultado:
Contexto conversacional usable.

---

# FASE 4 — GEMINI CORE (SEMÁNTICA)

Objetivo:
Sustituir heurísticas por inteligencia real.

### Implementar:

## Extract:
- intención
- empresa
- urgencia
- tipo de interacción

## Infer:
- oportunidad
- estado
- prioridad

## Generate:
- draft reply

### Importante:
Gemini NO escribe directamente en DB  
→ pasa por capa de validación

### Resultado:
Sistema entiende y redacta.

---

# FASE 5 — DRAFT SYSTEM

Objetivo:
Permitir interacción humana sobre output IA.

### Implementar:
- botón: Generate reply
- guardar draft (DB)
- opcional: Outlook drafts
- UI edición
- guardar / actualizar

### Resultado:
IA propone → humano edita.

---

# FASE 6 — SEND EMAIL

Objetivo:
Cerrar el loop operativo.

### Implementar:
- envío vía Microsoft Graph
- actualizar estado
- registrar sent_at
- persistir en CRM

### Resultado:
Sistema puede operar correo completo.

---

# FASE 7 — FIRST CONTACT SYSTEM

Objetivo:
Automatizar prospección controlada.

### Implementar:

## Modelo:
- FirstContactDraft

## Generación:
- límite diario

## Bandeja:
- /first-contact/

## Acciones:
- editar
- aprobar
- seleccionar
- enviar seleccionados

### Resultado:
Sistema genera outreach.

---

# FASE 8 — POLICY LAYER (CONTROL)

Objetivo:
Definir comportamiento del sistema.

### Configuración:

- daily_first_contact_generation_limit
- daily_send_limit
- allow_auto_draft
- allow_auto_send (OFF por defecto)
- categorías de correo
- reglas por tipo de interacción

### Resultado:
Automatización gobernada.

---

# FASE 9 — VECTOR MEMORY (IA FRIENDLY DB)

Objetivo:
Dar memoria real al sistema.

### Implementar:
- embeddings de:
  - emails
  - threads
  - empresas
  - oportunidades

## Retrieval:
- contexto relevante para Gemini

### Resultado:
IA con memoria contextual.

---

# FASE 10 — STRATEGIC CHAT (JARVIS V1)

Objetivo:
Interfaz de dirección estratégica.

### Capacidades:

## Consulta:
- estado del sistema
- resumen oportunidades
- riesgos

## Estrategia:
- recomendaciones
- enfoque comercial

## Comando:
- generar drafts
- crear acciones
- priorizar

## Memoria:
- aprender preferencias del usuario

### Restricción:
NO ejecución directa sin aprobación.

### Resultado:
CEO conversa con sistema.

---

# FASE 11 — AUTOMATION EXPANSION

Objetivo:
Incrementar autonomía progresivamente.

### Implementar:

- auto-draft según reglas
- auto-send en casos seguros
- confianza mínima
- detección de riesgo
- bloqueos automáticos

### Resultado:
Sistema empieza a operar solo.

---

# FASE 12 — FULL AI COMMERCIAL OS

Objetivo:
Sistema completo autónomo supervisado.

### Capacidades:

- gestión completa de email
- generación de oportunidades
- seguimiento automático
- campañas de first contact
- memoria semántica
- estrategia asistida por chat
- control total por el usuario

### Resultado final:

AI Sales Team completamente integrado donde:

- IA ejecuta
- usuario supervisa
- sistema aprende

---

## Estado actual (marzo 2026)

Completado:

- Pipeline completo
- Opportunity Intelligence V2
- Autotasking V1
- Prioritized UI
- Execution semantics
- Task detail governance UI

Progreso estimado:
70–75% del núcleo

---

## Próximo paso inmediato

FASE 1 — Governance base:
Revoke autotask + no recreate

---

## Filosofía de desarrollo

1. Primero control
2. Luego input real
3. Luego inteligencia
4. Luego automatización

---

## Nota final

Este proyecto no es un CRM.

Es un:

AI Commercial Operating System

