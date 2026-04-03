# NEXT SESSION — Core Closure Final

## Objetivo

Cerrar el core para producción real (sin supervisión).

---

## Bloques a implementar

### 1. Identidad canónica en inbound (CRÍTICO)

- asignar mailbox_account en entrada
- eliminar resolución heurística
- validación obligatoria

---

### 2. Idempotencia en execution

- evitar duplicados
- clave mínima:
  (recommendation_id + action_type)

---

### 3. Execution Log

- modelo ExecutionLog
- persistencia de:
  - request
  - result
  - status

---

### 4. Policy mínima

- permitir:
  - drafts
- bloquear:
  - send

---

## Restricciones

- no introducir plugins
- no tocar UI
- no introducir LLM

---

## Resultado esperado

Sistema capaz de:

- ejecutar acciones de forma segura
- evitar duplicados
- mantener trazabilidad completa
- operar sin supervisión

---

## Siguiente fase

👉 Plugin SMLL

Objetivo:

- entorno sandbox real
- envío controlado
- validación end-to-end

