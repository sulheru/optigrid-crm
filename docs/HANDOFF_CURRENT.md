# HANDOFF — CURRENT STATE

## Sistema: OptiGrid CRM — AI Commercial Operating System

---

## Estado actual

El sistema ya opera como un bucle comercial semiautónomo supervisable.

Pipeline operativo actual:

Inbound → AI Interpretation → Decision → Auto/Manual Apply → Action → Draft/Task/Opportunity Update → Approve → Send

---

## Componentes activos

### Inbox Intelligence V3
- análisis automático de inbound emails
- `InboundInterpretation` persistente
- `InboundDecision` persistente
- scoring
- priority
- risk flags
- auto-apply seguro
- auditoría básica de automatización

### Outbox V1.1
- drafts automáticos
- edición manual de subject y body
- approve / send
- bulk actions

### Tasks Supervisor Layer
- tareas auto y manuales visibles
- source / source_action visibles
- revocación operativa de tasks auto
- filtros de supervisor

### Opportunity System
- evolución por decisiones
- stage transitions manuales o derivadas del apply flow

---

## Lo validado en esta sesión

### Automation Layer V3
Validado desde navegador:

- caso seguro:
  - `send_information` → auto-apply OK
  - draft generado OK

- caso sensible:
  - `advance_opportunity` → manual OK

- caso rechazo:
  - `mark_lost` → manual OK

- dedupe observado sin duplicación inesperada en flujo probado

### Supervisor UX
- Inbox con visibilidad completa de decisión
- Tasks con visibilidad operativa mejorada
- filtros de supervisor en Inbox funcionando

---

## Estado de autonomía actual

### Auto-aplicable
- `send_information`
- `send_clarification`
- `schedule_followup` (si policy lo permite)

### Bloqueado para auto-apply
- `mark_lost`
- `advance_opportunity`

---

## Configuración actual

En `settings.py` existen flags activas para automatización inbound:

- `INBOX_AUTO_APPLY_ENABLED`
- `INBOX_AUTO_APPLY_SCORE_THRESHOLD`
- `INBOX_AUTO_BLOCKED_ACTIONS`
- `INBOX_AUTO_BLOCK_ON_RISK_FLAGS`

---

## Riesgos / limitaciones actuales

- policy sigue en `settings.py`, no en BD
- reversibilidad profunda aún incompleta
- layout UI global todavía no unificado
- persiste duplicación visual entre templates mientras no exista `base.html`
- dedupe es lógico, no por constraint SQL

---

## Estado general

✔ Estable  
✔ Funcional  
✔ Supervisable  
✔ Semiautónomo  
⚠ Aún sin shell UI común  
⚠ Aún sin settings operables desde BD  

---

## Ready for next phase

Sistema listo para:

👉 UI Foundation V1 (layout compartido + menú único)  
👉 Automation settings en BD  
👉 Governance / reversibility ampliada
