# ROADMAP — OPTIGRID CRM

## Fase actual
TENANT + MAILBOX SCOPING V1 COMPLETADA

---

## Fase siguiente — SIMULATED PERSONA V1

### Objetivo
Crear la base persistente de interlocutores simulados antes de implementar SMLL.

### Entregables
- Modelo SimulatedPersona
- Identidad del personaje:
  - nombre completo
  - cargo
  - empresa
  - seniority
- Perfil conductual:
  - formalidad
  - estilo de respuesta
  - tolerancia al riesgo
  - apertura al cambio
  - paciencia
- Contexto profesional:
  - objetivos
  - pains
  - prioridades
  - presupuesto implícito
- Estado dinámico:
  - interés
  - confianza
  - saturación
  - urgencia
  - frustración
- Base de prompt builder para respuestas futuras
- Vínculo con tenant simulado y mailbox simulado

---

## Fase siguiente — SMLL (Simulated Mail with LLM)

### Definición
Mail Provider implementado mediante LLM, apoyado sobre tenant simulado propio y personajes persistentes.

### Objetivo
Permitir pruebas end-to-end completas sin interacción con el mundo real y sin mezclar memoria con tenants reales.

### Componentes
- Simulated tenant
- Simulated mailbox accounts
- Simulated persona engine
- Simulated threads/messages
- Timing realista
- Respuestas coherentes con estado interno

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

## Principio clave

Compartir dentro de la empresa operadora.
Aislar entre empresas operadoras.
Simulador = tenant propio.
Persona simulada antes que correo simulado.
