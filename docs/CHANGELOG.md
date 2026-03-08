# Changelog — CRM IA-First

Este documento registra cambios importantes en el proyecto.

Sirve para entender:

- qué cambió
- cuándo cambió
- por qué cambió

---

# Formato

Fecha — Tipo — Descripción

Tipos:
- ARCHITECTURE
- MODEL
- MODULE
- FLOW
- DOCUMENTATION
- IMPLEMENTATION
- UI

---

# Registro

## 2026-03-08 — ARCHITECTURE

Se define arquitectura IA-first del sistema.

Documento creado:
docs/architecture/system_architecture.md

Impacto:
estructura completa del sistema.

---

## 2026-03-08 — MODEL

Se define modelo conceptual:

- entidades
- estados
- eventos

Documentos:

docs/data/entities.md  
docs/data/states.md  
docs/data/events.md

---

## 2026-03-08 — FLOW

Se definen flujos operativos principales:

- investigación de leads
- procesamiento de emails
- señal comercial → oportunidad

Documentos:

docs/flows/

---

## 2026-03-08 — MODULE

Se definen módulos funcionales principales:

- identidad M365
- integración de correo
- investigación IA
- actualización CRM
- consola conversacional

Documentos:

docs/modules/

---

## 2026-03-08 — DOCUMENTATION

Se crea sistema de continuidad documental:

- INDEX.md
- CHANGELOG.md
- NEXT_SESSION.md

---

## 2026-03-08 — IMPLEMENTATION

Se restaura el pipeline completo de procesamiento de emails.

Pipeline operativo:

EmailMessage → FactRecord → InferenceRecord → CRMUpdateProposal → AIRecommendation

Cambios principales:

- reparación de `services/email_ingest.py`
- reescritura de `apps/emailing/management/commands/demo_email_flow.py`
- creación de `apps/recommendations/services.py`
- integración de recomendaciones IA en el pipeline

---

## 2026-03-08 — UI

Se implementa la primera UI de inspección del pipeline.

Rutas añadidas:

- `/emails/`
- `/emails/<id>/`

Capacidades añadidas:

- listado de emails procesados
- navegación al detalle por email
- inspección de EmailMessage
- visualización de Facts
- visualización de Inferences
- visualización de CRMUpdateProposal
- visualización de AIRecommendation

Cambios técnicos principales:

- creación de `apps/emailing/urls.py`
- implementación de vistas en `apps/emailing/views.py`
- creación de templates:
  - `templates/emailing/email_list.html`
  - `templates/emailing/email_detail.html`
- activación del directorio global de templates en `config/settings.py`
- inclusión de rutas de emailing en `config/urls.py`

Resultado:
primera interfaz operativa para visualizar el “cerebro” del CRM IA-first.
