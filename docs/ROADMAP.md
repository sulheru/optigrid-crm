# Roadmap — OptiGrid CRM

## Estado actual

CORE: COMPLETADO

---

## Fase 2 — Entity & Identity Layer (EIL)

Objetivo:

Definir quién posee los datos y cómo se organiza el sistema.

Incluye:

- Organization model
- User model
- Email identity mapping
- Domain ownership resolution
- Multi-tenant base

---

## Fase 3 — SMLL (Sandbox Mail Loop Layer)

Objetivo:

Crear entorno cerrado de simulación de correo.

Incluye:

- mailbox interna
- loop inbound/outbound
- generación automática de eventos
- testing end-to-end

---

## Fase 4 — Inbound Real

Objetivo:

Conectar el sistema con el mundo real.

Incluye:

- IMAP / Gmail / M365 ingestion
- webhook ingestion
- normalización de emails

---

## Fase 5 — Outbound Real

Objetivo:

Ejecutar acciones reales.

Incluye:

- SMTP
- M365 send
- tracking de envíos

---

## Fase 6 — LLM Layer

Objetivo:

Aumentar capacidad de decisión del sistema.

Incluye:

- generación de respuestas
- clasificación avanzada
- aprendizaje continuo

---

## Principio rector

No añadir complejidad antes de tener contexto.

