# ROADMAP — OPTIGRID CRM

## Estado actual
SMLL STABLE + DJANGO CORE VERIFIED

---

## Fase siguiente — IDENTITY & CORPORATION LAYER V1

### Objetivo

Construir capa de identidad y corporación sobre tenancy existente.

---

### Principio clave

NO duplicar entidades existentes  
EXTENDER tenancy  
UNIFICAR modelo  

---

### Entregables

- Corporation
- CorporateDomain
- CorporateMembership

---

### Integración

- MailboxAccount (tenancy) ← extendido
- Resolución email → domain → corporation
- Contexto disponible para SMLL

---

## Fase siguiente — MULTI-TURN SMLL

- Persistencia de estado conversacional
- Evolución de confianza/interés

---

## Fase siguiente — PROVIDER REAL (M365)

- SOLO draft creation
- ejecución supervisada

---

## Principio global

Compartir dentro de empresa  
Aislar entre empresas  
Simulador = tenant propio  

