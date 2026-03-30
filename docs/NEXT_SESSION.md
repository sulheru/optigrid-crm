# NEXT SESSION — Identity & Corporation Layer V1

## Objetivo

Implementar la capa fundacional de identidad y corporación que permitirá:

- login corporativo
- múltiples empresas
- coherencia en SMLL
- base para providers reales (M365, SMTP)

---

## Alcance

### 1. Modelos mínimos

- Corporation
- CorporateDomain
- CorporateMembership

(opcionalmente IdentityEntity en versión simplificada)

---

### 2. Relaciones

- Corporation → Domains
- Domain → Mailboxes
- Identity → Membership → Corporation

---

### 3. Resolución por dominio

Implementar:

email → domain → corporation

---

### 4. Integración mínima con sistema actual

- MailboxAccount debe referenciar dominio o corporación
- SMLL debe poder acceder a CorporationProfile

---

### 5. No hacer en esta sesión

- UI
- CRM Update Engine
- Providers reales
- Multi-turn simulation

---

## Resultado esperado

- Soporte multi-corporación
- Base para login corporativo
- Estructura coherente para dominios y buzones
- SMLL contextualizado a nivel empresa

---

## Nota clave

Esta fase es fundacional. No debe mezclarse con UI ni providers.
