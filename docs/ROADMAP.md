# OptiGrid CRM — ROADMAP

## Estado actual

El sistema ya dispone de una base funcional relevante:

- modelo operativo CRM ya existente
- pipeline parcial email → intelligence → recommendation → task/opportunity
- execution layer funcional
- UI Foundation V2 avanzada pero no completamente auditada
- motor de scoring / ranking / urgency / NBA parcialmente implementado
- simulación de correo operativa
- capa estratégica con backend rule-based + Gemini fallback parcial

Sin embargo, el sistema aún no está gobernado de forma limpia a nivel backend.

La conclusión de la auditoría es clara:

- existe potencia real en el backend
- existe mezcla entre core, simulación, views y lógica operativa
- conviven más de un pipeline conceptual
- todavía no existe una capa unificada de providers
- el SOI (Scenario Orchestrator Interface) aún no está implementado
- Outlook real y Calendar real aún no están conectados

---

## Nueva dirección estratégica

Antes de implementar integraciones externas completas, el proyecto debe consolidar primero su backend canónico.

Principio rector:

**Primero núcleo estable. Después plugins.**

Esto implica:

1. consolidar pipeline canónico
2. separar core de adapters/providers
3. centralizar la inteligencia operativa
4. formalizar interfaces internas
5. introducir el SOI
6. conectar integraciones reales después

---

## FASE A — CONTROL Y CANONICAL BACKEND

### Objetivo
Convertir el backend actual en una base comprensible, coherente y gobernable.

### Metas
- definir cuál es el pipeline canónico del sistema
- aclarar la relación entre:
  - facts / inferences / proposals / recommendations
  - inbox intelligence / interpretation / decision / apply
- detectar duplicaciones de lógica
- separar mejor:
  - domain logic
  - application services
  - adapters
  - views
- consolidar la capa real de recommendations/NBA como servicio backend central

### Resultado esperado
Un backend con flujo canónico claro y con responsabilidades mejor separadas.

---

## FASE B — PROVIDER ABSTRACTION LAYER

### Objetivo
Preparar el sistema para trabajar con providers intercambiables.

### Contratos a definir
- MailProvider
- LLMProvider
- CalendarProvider

### Metas
- sacar la simulación del core y moverla a adapter explícito
- evitar que views o servicios de dominio dependan directamente de Outlook, Gemini o simuladores
- formalizar interfaces mínimas de backend
- introducir implementaciones stub/simulated donde haga falta

### Resultado esperado
Sistema preparado para enchufar backends reales sin contaminar el núcleo.

---

## FASE C — SCENARIO ORCHESTRATOR INTERFACE (SOI)

### Objetivo
Introducir una capa de gobierno de escenario y modo de ejecución.

### Responsabilidades previstas del SOI
- seleccionar escenario operativo
- decidir modo:
  - simulation
  - real
  - hybrid
- resolver qué provider usar en cada operación
- gobernar políticas de ejecución y trazabilidad
- permitir coexistencia de entornos simulados y reales

### Resultado esperado
Punto central de orquestación del sistema.

---

## FASE D — REAL INTEGRATIONS

### Objetivo
Conectar providers reales una vez estabilizado el backend.

### Integraciones previstas
- Outlook / Microsoft Graph Mail
- Outlook Calendar
- proveedor LLM generalizado
- contactos / calendario / correo sincronizados

### Nota
Calendar no se concibe solo como agenda, sino también como canal útil de notificaciones reales hacia móvil.

### Resultado esperado
Sistema con backend real conectado al exterior.

---

## FASE E — EXECUTIVE SURFACES

### Objetivo
Exponer el backend ya consolidado en superficies ejecutivas coherentes.

### Superficies
- Dashboard
- Recommendations
- Strategic Chat
- alerting / reminders / notifications

### Resultado esperado
Producto IA-first coherente, donde la UI refleje realmente el cerebro backend.

---

## Orden recomendado

1. FASE A — CONTROL Y CANONICAL BACKEND
2. FASE B — PROVIDER ABSTRACTION LAYER
3. FASE C — SOI
4. FASE D — REAL INTEGRATIONS
5. FASE E — EXECUTIVE SURFACES

---

## Prioridad actual

**PRIORIDAD ABSOLUTA: BACKEND**

No empezar todavía por plugins completos.
No empezar todavía por Outlook real.
No empezar todavía por Calendar real.
No empezar todavía por SOI completo.

Primero:
- controlar
- unificar
- abstraer
- estabilizar

