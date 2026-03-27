# ROADMAP — EXTERNAL ACTIONS

## FASE 1 — STABILIZATION (COMPLETADA)

✔ eliminar auto-dispatch  
✔ eliminar recursión  
✔ asegurar idempotencia  
✔ estabilizar tests  

---

## FASE 2 — CONTROL LAYER (SIGUIENTE)

- approval flow
- estados de aprobación
- UI mínima (opcional)

---

## FASE 3 — EXECUTION LAYER

- dispatcher explícito
- logging de ejecución
- manejo de errores

---

## FASE 4 — PROVIDERS

- email (Microsoft Graph / SMTP)
- abstracción de providers
- retry + fallback

---

## FASE 5 — POLICY ENGINE

- qué requiere aprobación
- qué puede auto-ejecutarse
- límites de seguridad

---

## FASE 6 — AUTOMATION (FUTURO)

- auto-exec controlado
- reglas configurables
- observabilidad

---

## PRINCIPIO FUNDAMENTAL

"Nada se ejecuta sin control explícito"

