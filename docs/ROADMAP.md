# ROADMAP — OptiGrid CRM
## AI Commercial Operating System

---

## VISIÓN

Construir un sistema donde:

- la IA ejecuta funciones comerciales completas en background
- el usuario actúa como CEO / supervisor
- el sistema detecta señales, investiga cuentas, genera hipótesis y propone o ejecuta acciones
- el pipeline CRM se alimenta automáticamente
- el correo será el canal real de interacción externa
- la gobernanza decide qué se autoejecuta y qué requiere aprobación humana

OptiGrid no es un CRM tradicional.

Es un **AI Commercial Operating System**.

---

## PRINCIPIOS RECTORES

### 1. IA como operador principal
La IA debe encargarse de:
- investigar empresas
- detectar señales
- estructurar información
- generar recomendaciones
- crear tareas
- preparar borradores
- priorizar acciones
- ejecutar todo lo no crítico

### 2. Humano como supervisor estratégico
El usuario no debe operar manualmente el CRM.
Debe intervenir principalmente para:
- aprobar decisiones sensibles
- validar envíos externos
- definir precio o alcance
- aceptar o rechazar decisiones estratégicas

### 3. Separación semántica
- Facts ≠ Inferences ≠ Decisions
- El sistema debe preservar esa separación en toda automatización

### 4. Automatización por defecto
La pregunta base no es:
“qué automatizamos”
sino:
“qué necesita validación humana”

### 5. Gobernanza obligatoria
Toda acción relevante debe:
- tener rationale
- dejar trazabilidad
- respetar policy mode
- poder auditarse

### 6. Memoria operativa
El sistema debe recordar:
- qué ya vio
- qué descartó
- qué aprobó
- qué ejecutó
- qué no debe repetir

---

## ARQUITECTURA OBJETIVO

1. Communication Layer
2. Operational CRM Core
3. Target Intelligence Layer
4. Strategy Layer (Jarvis)
5. Governance Layer
6. Outbound Engine
7. Execution & Workflow Engine

---

## FASE 0 — OPERATIONAL CRM CORE ✅

### Incluye
- Pipeline completo:
  Email → Fact → Inference → Proposal → Recommendation → Task → Opportunity
- Recommendation system
- Task system
- Opportunity model
- UI básica operativa

### Estado
DONE

### Resultado
Base CRM funcional y ya orientada a IA.

---

## FASE 1 — OPPORTUNITY INTELLIGENCE ✅

### Incluye
- scoring
- priority
- risk_flags
- next_actions
- análisis batch
- reuse de recommendations
- reuse de tasks

### Estado
DONE

### Resultado
El sistema ya sabe valorar oportunidades activas y proponer foco operativo.

---

## FASE 2 — GOVERNANCE BASE ✅

### Incluye
- revocación manual de tasks
- persistencia de decisiones humanas
- bloqueo de recreación automática
- respeto de `is_revoked` en autotasker

### Estado
DONE

### Resultado
Autonomía inicial con control humano efectivo.

---

## FASE 3 — STRATEGY LAYER (JARVIS) 🟡

### Objetivo
Crear una interfaz de dirección estratégica del sistema.

### Ya implementado
- Strategy Chat V1
- Strategy Chat V1.1
- chat conectado a contexto real del CRM
- respuesta estructurada:
  - prioridades
  - riesgos
  - acciones recomendadas

### En curso
- Strategy Chat V2
- backend LLM opcional
- fallback rule-based

### Próximo
- contexto ampliado
- tools de lectura
- trazabilidad de backend
- daily prioritization real

### Resultado esperado
Jarvis puede responder:
- qué hacer hoy
- dónde enfocarse
- qué está bloqueado
- qué oportunidades tienen más potencial
- qué gaps operativos existen

### Estado
IN PROGRESS

---

## FASE 4 — TARGET INTELLIGENCE LAYER 🔵

### Objetivo
Pasar de “buscar empresas” a “generar oportunidades argumentadas y accionables”.

### 4.1 Signal Discovery
La IA debe detectar cuentas objetivo a partir de señales como:
- funding
- hiring
- expansión
- partnerships
- lanzamientos
- crecimiento observable
- señales de dolor operacional

#### Salidas
- LeadSuggestion
- LeadSignal

### 4.2 Account Enrichment
La IA debe enriquecer cada cuenta con:
- perfil de empresa
- localización
- tamaño estimado
- vertical
- buyer roles probables
- madurez
- stack o entorno estimado
- contexto comercial

#### Salidas
- LeadResearchSnapshot

### 4.3 Commercial Hypothesis
Para cada cuenta, la IA debe producir:
- por qué ahora
- problema probable
- encaje con OptiGrid
- urgencia estimada
- siguiente acción recomendada

### 4.4 Ranking Engine
Scoring basado en:
- fit
- timing
- novedad
- accionabilidad
- confianza

### 4.5 Intelligence Inbox
Bandeja operativa con acciones:
- approve
- dismiss
- reopen
- view detail
- materialize to CRM

### Resultado esperado
La IA ya no genera solo empresas sugeridas.
Genera **tesis comerciales accionables**.

### Estado
NEXT MAJOR BLOCK

---

## FASE 5 — CRM INJECTION BRIDGE 🟣

### Objetivo
Convertir inteligencia en pipeline CRM real.

### Capacidades
Al aprobar o autoaceptar una sugerencia:
- crear o reutilizar Company
- registrar Facts
- registrar Inferences
- crear Recommendation
- crear CRMTask
- opcionalmente abrir Opportunity preliminar

### Resultado esperado
Research → Pipeline automático

### Estado
PLANNED

---

## FASE 6 — GOVERNED ACTION LAYER 🔴

### Objetivo
Permitir que la IA actúe con políticas explícitas.

### Capacidades
- ActionProposal
- policy engine
- clasificación por acción:
  - safe_auto
  - approval_required
  - forbidden
- trazabilidad de propuestas y ejecuciones

### Ejemplos
- create_task → safe_auto
- create_recommendation → safe_auto
- create_opportunity_preliminary → approval_required
- send_email → approval_required al inicio

### Resultado esperado
La IA opera con límites claros y auditables.

### Estado
PLANNED

---

## FASE 7 — JARVIS OPERATIVO 🟠

### Objetivo
Jarvis no solo aconseja; también consulta y opera.

### Capacidades
#### Lectura
- pipeline snapshot
- opportunity detail
- lead suggestions
- tasks
- recommendations
- research context
- outbound queue

#### Escritura gobernada
- create_task
- create_recommendation
- create_opportunity
- aprobar sugerencia
- generar draft
- lanzar investigación adicional

### Resultado esperado
Jarvis funciona como jefe de ventas IA con acceso estructurado al sistema.

### Estado
PLANNED

---

## FASE 8 — OUTBOUND ENGINE 🟤

### Objetivo
Automatizar primer contacto y seguimiento inicial.

### Capacidades
- generación de first contact emails
- follow-up emails
- cola dedicada de outbound
- control de volumen diario
- segmentación
- aprobación configurable
- integración futura con Outlook

### Resultado esperado
La IA inicia conversaciones comerciales reales.

### Estado
PLANNED

---

## FASE 9 — COMMUNICATION LAYER / OUTLOOK INTEGRATION ⚫

### Objetivo
Usar el correo real como canal principal del sistema.

### Capacidades
- lectura automática de inbox
- clasificación
- asociación a empresa/contacto/oportunidad
- extracción automática a Facts / Inferences
- preparación de drafts
- seguimiento de respuestas
- actualización del pipeline desde interacción real

### Resultado esperado
El sistema conecta investigación, estrategia y ejecución con el canal real de comunicación.

### Estado
PLANNED

---

## FASE 10 — EXECUTION & WORKFLOW ENGINE ⚙️

### Objetivo
Mover el sistema a operación continua en background.

### Capacidades
- workflows asíncronos
- scheduling de discovery
- enriquecimiento automático
- daily prioritization
- draft generation
- reprocesado
- retries
- event-driven orchestration

### Resultado esperado
El sistema trabaja de manera continua sin bloquear la operación manual.

### Estado
PLANNED

---

## FASE 11 — FULL AUTONOMY LOOP 🚀

### Objetivo
Cerrar el loop comercial completo.

### Loop objetivo
1. Detecta señales
2. Investiga cuentas
3. Genera hipótesis
4. Prioriza
5. Materializa en CRM
6. Crea acciones
7. Prepara contacto
8. Aprende del histórico
9. Reitera

### Resultado final
Sistema comercial autónomo end-to-end donde el humano solo interviene en decisiones críticas.

### Estado
VISION TARGET

---

## MODELO OPERATIVO FINAL

### La IA gestiona
- discovery
- research
- memoria operativa
- priorización
- propuestas
- tareas
- drafts
- seguimiento
- pipeline hygiene
- parte creciente de la ejecución

### El humano gestiona
- decisiones críticas
- envíos sensibles
- pricing
- alcance
- validación estratégica
- excepciones

---

## SIGUIENTE PASO INMEDIATO

### Prioridad recomendada
FASE 4 — Target Intelligence Layer

### Primera subfase
Implementar:

- LeadSuggestion model
- LeadSignal model
- LeadResearchSnapshot model
- schema validado
- signal discovery engine
- lead memory service
- background task
- intelligence inbox mínima

### Motivo
Es el punto de entrada del sistema autónomo y el bloque que alimenta:
- strategy
- pipeline
- outbound
- workflows

---

## DEFINICIÓN DE ÉXITO

El sistema estará funcionando como AI Commercial OS cuando:

- descubra oportunidades sin intervención manual
- evite repetición y ruido
- justifique por qué actuar ahora
- priorice correctamente
- convierta inteligencia en objetos CRM útiles
- ejecute acciones seguras automáticamente
- pida aprobación solo en decisiones críticas

---

## CONCLUSIÓN

OptiGrid deja de ser:

CRM con automatizaciones parciales

y pasa a ser:

**Sistema operativo comercial autónomo con supervisión humana estratégica**
