# NEXT SESSION — Identity & Corporation Layer V1 (Corrected)

## Objetivo

Implementar la capa de identidad y corporación sobre el sistema real existente.

---

## Contexto actualizado

MailboxAccount ya existe en tenancy.

La nueva capa debe integrarse sobre él.

---

## Alcance

### Modelos a crear

- Corporation
- CorporateDomain
- CorporateMembership

(opcional: IdentityEntity simplificado)

---

## Relaciones

- Corporation → Domains
- Domain → MailboxAccount (existente)
- Membership → Corporation

---

## Resolución clave

email → domain → corporation

---

## Integración

- MailboxAccount debe:
  - referenciar dominio o corporación
- SMLL debe:
  - poder acceder a Corporation context

---

## Restricciones

NO:
- crear MailboxAccount nuevo
- tocar UI
- tocar providers reales
- implementar CRM Update Engine

---

## Resultado esperado

- Multi-corporation base funcional
- Resolución por dominio operativa
- SMLL contextualizado por empresa
- Base para login corporativo

---

## Nota crítica

Esta sesión es fundacional.

Errores aquí comprometen todo el sistema.

