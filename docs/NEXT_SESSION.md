# NEXT SESSION PROMPT

PROYECTO: OptiGrid CRM — AI Commercial Operating System

---

## CONTEXTO

Estamos construyendo un sistema IA-first donde:

- la IA ejecuta funciones comerciales completas
- el usuario actúa como CEO / supervisor
- el sistema ya gestiona:
  - Dashboard
  - Strategic Chat
  - Mailing
    - Outbox
    - Inbox
  - Recommendations
  - Tasks
  - Opportunities
  - Leads

Pipeline comercial operativo actual:

Inbound → AI Interpretation → Decision → Auto/Manual Apply → Action → Draft/Task/Opportunity Update → Approve → Send

---

## ESTADO ACTUAL DEL SISTEMA

### Backend
✔ Automation Layer V3 implantado  
✔ scoring / priority / risk flags persistidos  
✔ auto-apply seguro validado  
✔ blocked actions respetadas  
✔ tests OK  

### UI
✔ Inbox Supervisor UI  
✔ Tasks Supervisor UI  
✔ Inbox Supervisor Filters  
⚠ aún no existe layout común compartido  
⚠ navegación duplicada entre templates  

---

## OBJETIVO DE LA SIGUIENTE SESIÓN

Implementar **UI FOUNDATION V1**

Crear un layout compartido y un menú global reutilizable para toda la aplicación.

---

## REQUISITOS

### 1. Shared Base Layout
Crear:

- `templates/base.html`
- estructura común de app shell
- bloque principal de contenido
- estilos globales mínimos y reutilizables

### 2. Global Navigation
Crear un menú único compartido con estas secciones:

- Dashboard
- Strategic Chat
- Mailing
  - Outbox
  - Inbox
- Recommendations
- Tasks
- Opportunities
- Leads

### 3. Primera migración de vistas
Migrar primero estas vistas a `base.html`:

- Inbox
- Outbox
- Tasks

### 4. Active section highlighting
Resaltar en navegación la vista o sección activa.

### 5. No romper funcionalidad
Mantener intacto:

- filtros actuales
- forms POST
- apply / dismiss
- outbox actions
- revoke task

---

## RESTRICCIONES

- no rehacer toda la UI
- no introducir complejidad innecesaria
- no meter JS complejo
- no hacer design system completo todavía
- mantener compatibilidad con templates existentes

---

## OUTPUT ESPERADO

- `base.html`
- parcial o bloque reutilizable de navegación
- Inbox / Outbox / Tasks migrados al shell común
- estilos comunes básicos
- validación visual funcional

---

## OBJETIVO ESTRATÉGICO

Pasar de múltiples pantallas aisladas
→ a una aplicación coherente con shell de producto

Preparar el terreno para:
- settings operables
- dashboard real
- strategy cockpit
- governance layer visual
