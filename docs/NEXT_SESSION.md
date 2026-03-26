# NEXT SESSION — PORT SYSTEM V1

## Contexto

Sistema con NBA Engine consolidado y core estable.

Necesidad:

Abrir el sistema a integraciones externas sin perder control.

---

## Objetivo

Diseñar formalmente el sistema de puertos (nivel producción).

NO implementar.

---

## Alcance

### 1. ExternalActionIntent

- definición completa de entidad
- campos
- estados
- relación con Recommendation / Task

---

### 2. Policy Gate

- reglas por tipo de acción
- human-in-the-loop obligatorio
- clasificación de acciones críticas

---

### 3. Port Router

- mapping intent → adapter
- resolución dinámica

---

### 4. ExternalPort Contract

- interfaz base
- normalización de resultados
- idempotencia

---

### 5. Adapter Model

- separación puerto vs adapter
- M365 como primer caso

---

### 6. Event Model

- ciclo completo de intención externa
- trazabilidad

---

## Reglas

- no implementar código funcional
- no tocar execution layer existente
- no introducir complejidad innecesaria
- mantener coherencia con arquitectura actual

---

## Resultado esperado

Documento de arquitectura sólido:

PORT SYSTEM V1 — SPEC listo para implementación en sesiones futuras
