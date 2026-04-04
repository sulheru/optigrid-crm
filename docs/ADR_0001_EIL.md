# ADR-0001 — Entity & Identity Layer

## Estado

Accepted

---

## Contexto

El sistema era email-driven pero carecía de:

- identidad
- ownership
- multi-tenancy
- modelo de usuarios y entidades

Esto bloqueaba:

- coherencia del CRM
- escalabilidad
- integraciones externas

---

## Decisión

Se introduce EIL con:

### Entidades principales

- OperatingOrganization (tenant)
- Domain
- EmailIdentity
- User
- Membership
- Company
- Contact
- Candidate layer

---

## Principios

- email como raíz de identidad
- sistema event-driven
- separación estricta:
  - identity ≠ CRM
  - provider ≠ truth
- diseño mínimo pero extensible

---

## Consecuencias

### Positivas

- multi-tenant sólido
- base para control de acceso
- integración limpia con providers
- soporte para simulación (SMLL)

### Negativas

- mayor complejidad inicial
- necesidad de resolver identidad en ingestión

---

## Decisiones relacionadas

- SMLL usa sandbox + `.sim`
- contactos son híbridos (persona / rol)
- candidates evitan contaminación

