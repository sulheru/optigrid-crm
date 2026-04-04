# SESSION LOG — 2026-04-04

## Tipo de sesión

Diseño arquitectónico — Entity & Identity Layer (EIL)

---

## Objetivo

Definir:

- modelo de entidades
- identidad basada en email
- ownership del CRM
- base multi-tenant
- integración futura con providers
- base para SMLL

---

## Decisiones clave

### Identity

- Email como raíz de identidad
- EmailIdentity como entidad canónica
- Domain como entidad explícita

---

### Tenancy

- OperatingOrganization como tenant
- aislamiento total
- todo dato pertenece a una organización

---

### CRM

- separación:
  - Organization ≠ Company
- Contact = interlocutor (no solo persona)

---

### Candidate Layer

- CompanyCandidate
- ContactCandidate

Objetivo:
- evitar contaminación del CRM

---

### Providers

- M365 / Google:
  - contactos referenciados (no canónicos)
- SMTP / SMLL:
  - contactos internos

---

### Monetización

- definida en OperatingOrganization

---

### LLM Context

- descripción de organización
- objetivos
- tono

---

### SMLL

- sandbox obligatorio
- dominio `.sim`
- aislamiento completo

---

### Automatizaciones

- modelo basado en:
  - descripción humana
  - switch

---

## Resultado

Sistema preparado para:

- multi-tenant real
- inbound automático
- simulación segura
- evolución IA

