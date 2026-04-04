# ROADMAP — NEXT

## Fase inmediata

### 1. EIL — Implementación

- models.py:
  - OperatingOrganization
  - Domain
  - EmailIdentity
  - User
  - Membership
  - Company
  - Contact
  - Candidates

- servicios:
  - resolve_email_identity()
  - resolve_organization()
  - create_provisional_organization()

---

### 2. Integración mínima

- conectar inbound email → EIL
- asignar organization en ingestión

---

## Fase siguiente

### 3. SMLL

- organizaciones sandbox
- generación `.sim`
- simulación de inbox/outbox
- personas simuladas

---

### 4. Automatizaciones (base)

- modelo AutomationRule
- storage
- switch básico

---

## Fase posterior

- Domain verification
- Ownership claims
- UI mínima
- Integración M365 / Google
- Lead enrichment avanzado
- scoring de oportunidades

