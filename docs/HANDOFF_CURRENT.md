# OptiGrid CRM — HANDOFF NEXT

## Estado actual

El core del sistema está completamente cerrado y validado:

- Rule Engine determinista
- Explainability
- Decision Output
- Execution Engine (drafts only)
- Provider abstraction
- Recommendation Bridge
- Idempotencia

Se ha diseñado completamente la capa:

👉 Entity & Identity Layer (EIL)

---

## Qué existe conceptualmente (no implementado aún)

### Identidad / Tenancy

- OperatingOrganization (tenant canónico)
- Domain
- EmailIdentity
- Membership
- User

### CRM

- Company
- Contact (interlocutor híbrido)
- Candidate layer (CompanyCandidate, ContactCandidate)

### LLM Context

- organization.description
- organization.llm_context_summary

### Monetización

- plan_type
- plan_status
- is_internal

---

## SMLL definido

- organizaciones sandbox
- dominios `.sim`
- aislamiento total
- herencia de perfil, no de identidad

---

## Automatizaciones (visión)

- lista con descripción humana
- switch on/off
- preparado para evolución futura

---

## Siguiente paso

👉 IMPLEMENTACIÓN EIL (Django models + servicios mínimos)

Sin:

- login
- permisos complejos
- UI

