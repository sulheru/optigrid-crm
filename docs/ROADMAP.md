# ROADMAP — OPTIGRID CRM

## Fase actual
Provider-aware execution layer COMPLETADA

---

## Fase siguiente — VISIBILITY (UI / ADMIN)

### Objetivo
Dar visibilidad operativa total al sistema antes de conectar providers reales.

### Entregables
- Admin de ExternalActionIntent
- Visualización de normalized_preview
- Inspección de payload (pretty)
- Filtros por:
  - type
  - status
  - provider
- Base para human-in-the-loop

---

## Fase siguiente — SMLL (Simulated Mail with LLM)

### Definición
Mail Provider implementado mediante LLM.  
El sistema y el usuario no distinguen entre SMLL y proveedores reales.

### Objetivo
Permitir pruebas end-to-end completas sin interacción con el mundo real.

### Componentes

#### 1. SMLL Provider
- create_draft()
- send()
- fetch_inbound()

#### 2. LLM Contact Agent
- Generación de respuestas realistas
- Contexto de hilo
- Personalidad configurable

#### 3. Simulated Mail World (persistente)
- simulated_accounts
- simulated_contacts
- simulated_threads
- simulated_messages

#### 4. Timing realista
- delays
- no-responses
- followups naturales

### Capacidades
- Simulación de ciclos completos:
  outbound → inbound → CRM updates → recommendations
- Testing reproducible
- Exploración de edge cases

---

## Fase siguiente — PROVIDER REAL (M365)

### Objetivo
Conectar ejecución real manteniendo control.

### Alcance inicial
- SOLO draft creation (no send)

### Restricciones
- email.send sigue bloqueado
- ejecución bajo supervisión

---

## Fase siguiente — INTELLIGENCE LOOP

### 1. LLM refinement
- edición de drafts
- chat contextual sobre intents

### 2. Knowledge integration
- uso de vector memory
- aprendizaje continuo

---

## Fase futura — EXECUTION

### 1. Human-in-the-loop send
- aprobación manual
- envío controlado

### 2. Automatización parcial
- reglas seguras
- bajo riesgo

---

## Principio clave

NUNCA automatizar acciones irreversibles sin control humano.

SMLL actúa como entorno operativo seguro para validar el sistema completo antes de interactuar con el mundo real.

