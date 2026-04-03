# OptiGrid CRM — ROADMAP

---

## Estado actual

Sistema en:

👉 Producción controlada

Capas cerradas:

- Decision Engine ✔
- Trace & Explainability ✔
- Decision Output ✔
- Execution Engine (mínimo) ✔
- Provider abstraction ✔

Capas pendientes:

- identidad inbound
- idempotencia
- execution logging
- policy

---

# PHASE 1 — CORE CLOSURE (FINAL)

## Objetivo

Pasar de:

👉 Producción controlada  
a  
👉 Producción real (sin supervisión)

---

## 1. Identidad canónica en inbound (CRÍTICO)

### Problema

InboundEmail puede existir sin:

- mailbox_account
- operating_organization

### Solución

- asignación obligatoria en entrada
- eliminar resolución heurística
- validación dura

### Resultado

- consistencia multi-tenant
- eliminación de ambigüedad

---

## 2. Idempotencia en execution

### Problema

Ejecuciones duplicadas posibles

### Solución

- clave de idempotencia:
  (recommendation_id + action_type)

- verificación antes de ejecutar

### Resultado

- eliminación de duplicados
- ejecución segura

---

## 3. Execution Log

### Problema

No hay trazabilidad de ejecución

### Solución

Modelo:

ExecutionLog:
- request
- result
- status
- timestamps

### Resultado

- auditabilidad
- debugging real
- base para replay

---

## 4. Policy mínima

### Problema

No hay control de acciones

### Solución

- permitir:
  - drafts
- bloquear:
  - send

### Resultado

- seguridad operativa
- control de riesgo

---

## Resultado de Phase 1

Sistema capaz de:

- operar sin supervisión
- ejecutar acciones con seguridad
- mantener trazabilidad completa
- garantizar identidad consistente

---

# PHASE 2 — SMLL PLUGIN (SANDBOX)

## Objetivo

Introducir primer provider real:

👉 SMLL (Simple Mail Local Layer)

---

## Funcionalidad

- envío real en entorno controlado
- almacenamiento local de mensajes
- simulación de entrega

---

## Capacidades

- send email (sandbox)
- draft → send flow completo
- tracking de envíos

---

## Resultado

- validación end-to-end
- entorno seguro de pruebas
- base para providers reales

---

# PHASE 3 — PROVIDERS REALES

## Objetivo

Integración con:

- SMTP
- Gmail API
- Microsoft 365

---

## Requisitos

- retry logic
- error handling
- rate limiting
- autenticación segura

---

## Resultado

- sistema listo para producción externa

---

# PHASE 4 — AUTOMATIZACIÓN CONTROLADA

## Objetivo

Permitir ejecución automática

---

## Componentes

- policy engine avanzado
- niveles de riesgo
- aprobación humana opcional

---

## Resultado

- automatización progresiva
- control total de acciones

---

# PHASE 5 — LLM INTEGRATION

## Objetivo

Introducir IA en:

- generación de respuestas
- clasificación avanzada
- sugerencias dinámicas

---

## Restricciones

- siempre sobre execution engine
- nunca acoplado directamente a providers

---

## Resultado

- sistema inteligente + seguro

---

# PHASE 6 — UI & OPERATIONS

## Objetivo

Visibilidad y control

---

## Componentes

- execution dashboard
- audit logs UI
- control manual de acciones
- monitoring

---

## Resultado

- sistema operable por humanos

---

# PRINCIPIOS CLAVE

1. decision ≠ execution ≠ provider
2. identidad siempre desde BD
3. no heurísticas en producción
4. no acciones irreversibles sin control
5. execution siempre trazable

---

# RESUMEN

Estado actual:

👉 Core casi cerrado

Siguiente paso:

👉 cerrar core completamente

Después:

👉 SMLL → sandbox real

