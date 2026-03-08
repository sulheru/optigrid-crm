# NEXT SESSION

## Estado actual

Pipeline IA-first operativo y ya visible desde navegador.

Actualmente existe:

- pipeline funcional:
  - EmailMessage
  - FactRecord
  - InferenceRecord
  - CRMUpdateProposal
  - AIRecommendation
- comando demo funcional
- UI mínima de inspección:
  - `/emails/`
  - `/emails/<id>/`

---

## Objetivo de la próxima sesión

Hacer la segunda iteración de la UI del CRM.

---

## Tareas

### 1. Mejorar lista de emails

Ruta:

`/emails/`

Añadir o refinar:

- conteo de facts
- conteo de inferences
- conteo de proposals
- conteo de recommendations
- navegación más clara al detalle

---

### 2. Refinar vista de detalle

Ruta:

`/emails/<id>/`

Mejorar:

- legibilidad visual
- agrupación por bloques
- presentación más clara del body
- presentación más clara de facts / inferences / proposals / recommendations

---

### 3. Crear dashboard mínimo

Ruta sugerida:

`/`

Mostrar:

- total de emails procesados
- recomendaciones activas
- propuestas recientes
- accesos rápidos a emails recientes

---

### 4. Preparar siguiente capa UI

Evaluar diseño para estas vistas futuras:

- `/recommendations/`
- `/tasks/`
- `/opportunities/`

---

## Objetivo

Pasar de una UI meramente funcional a una UI operativa mínima del CRM.

La siguiente sesión no debe ir todavía a frontend complejo.
Debe consolidar primero una interfaz útil, clara y navegable con Django templates.
