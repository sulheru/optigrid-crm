# NEXT SESSION PROMPT

PROYECTO: OptiGrid CRM — AI Commercial Operating System

---

## CONTEXTO

Sistema IA-first donde:

- IA ejecuta funciones comerciales
- Usuario supervisa (CEO mode)
- Sistema gestiona:
  - inbox
  - outbox
  - oportunidades
  - tareas

Pipeline actual:

Inbound → AI → Decision → Apply → Draft → Edit → Approve → Send

---

## ESTADO ACTUAL

✔ Inbox Intelligence V2 completo  
✔ Outbox editable  
✔ Apply/Dismiss funcionando  
✔ Tests OK  

Sistema funcional end-to-end

---

## OBJETIVO DE LA SESIÓN

Implementar AUTOMATION LAYER (V3)

---

## REQUISITOS

### 1. Auto Apply Decisions

- aplicar automáticamente si:
  - requires_approval = False
  - confidence > threshold

### 2. Decision Scoring

Añadir a InboundDecision:

- score
- risk_flags
- priority

---

### 3. Deduplication

- evitar generar múltiples decisiones iguales
- hash por:
  - inbound_id
  - action_type

---

### 4. Logging / Audit

- registrar:
  - decisiones aplicadas automáticamente
  - origen

---

## RESTRICCIONES

- No romper V2
- Mantener control manual
- Todo reversible

---

## OUTPUT ESPERADO

- servicios nuevos
- cambios en modelo (si necesario)
- integración limpia
- tests básicos

---

## NOTA

Sistema ya funciona.
Ahora el objetivo es reducir intervención humana sin perder control.

