# NEXT SESSION — Knowledge Harvest Pipeline V1

## Objetivo

Construir el sistema de aprendizaje del CRM:

👉 La IA observa → aprende → propone → humano valida

---

## Alcance

### 1. Email ingestion semántica

- leer inbound emails
- extraer:
  - posibles preguntas
  - posibles respuestas
  - patrones operativos

---

### 2. Memoria vectorial (V1 simple)

- almacenar embeddings
- permitir similitud
- base para clustering

---

### 3. Knowledge Candidates

Nuevo modelo:

- tipo:
  - FAQ
  - BEHAVIOR
  - CAPABILITY_PROPOSAL
- contenido propuesto
- confidence_score
- source_examples
- status: proposed

---

### 4. Generator service

Servicio que:

- detecta recurrencias
- genera candidates automáticamente

---

### 5. Review mínima (sin UI compleja)

- aceptar
- rechazar
- promover a KB

---

## Reglas

- ❌ NO auto-learning a KB directa
- ❌ NO auto-activation
- ✅ humano valida todo
- ✅ vectorial = sugerencia, no verdad

---

## Resultado esperado

Sistema capaz de decir:

"He aprendido X. ¿Quieres que lo use a partir de ahora?"

