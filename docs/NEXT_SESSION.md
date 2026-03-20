# NEXT SESSION — Inbox Intelligence V2

## CONTEXTO

Inbox Intelligence V1 está implementado:

InboundEmail → Interpretation → Decision (suggested)

Actualmente:
- Interpretación automática
- Decisión sugerida visible
- Sin ejecución automática

---

## OBJETIVO DE LA SESIÓN

Convertir inbox en motor de acción:

👉 Implementar APPLY DECISION

---

## FEATURES A IMPLEMENTAR

### 1. Apply Inbound Decision

Nueva acción:

apply_inbound_decision(decision)

Debe permitir:

- crear task (follow-up)
- generar draft de respuesta
- avanzar opportunity stage
- marcar como lost
- solicitar más info

---

### 2. Endpoint

POST /inbox/<id>/apply-decision/

---

### 3. UI

Botón en inbox:

[Apply Decision]

Estados:

- suggested → applied
- suggested → dismissed

---

### 4. Seguridad

- requires_approval flag respetado
- logging de acciones

---

### 5. Opcional (stretch)

- auto-apply si confidence > threshold
- configuración por tipo de email

---

## RESULTADO ESPERADO

Sistema cerrado:

OUTBOUND → INBOUND → UNDERSTAND → DECIDE → ACT → OUTBOUND

👉 Loop comercial autónomo

