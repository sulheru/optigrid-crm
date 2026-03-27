# NEXT SESSION — PLAN

## OBJETIVO

Construir Execution Pipeline completo (Approval + Dispatch)

---

## PRIORIDADES

### 1. Approval Flow (MVP)

- integrar approval_required
- endpoint / método:
  approve_external_action_intent

- transición:
  READY_TO_EXECUTE → APPROVED

---

### 2. Dispatcher limpio

- función explícita:
  dispatch_external_action_intent(intent)

- sin efectos secundarios
- sin auto-trigger

---

### 3. Integración mínima email provider

- mock o stub provider
- preparar interfaz:
  send_email_draft / create_draft

---

### 4. Estado del Intent

Definir claramente:

- NEW
- READY_TO_EXECUTE
- APPROVED
- EXECUTED
- FAILED

---

## NO HACER

- no automatizar ejecución aún
- no añadir complejidad innecesaria
- no introducir LLM en ejecución

---

## CRITERIO DE ÉXITO

Pipeline completo:

Recommendation
→ Intent
→ Approval
→ Dispatch manual
→ Resultado consistente

