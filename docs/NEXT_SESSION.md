# NEXT SESSION OBJECTIVES

## Objetivo principal
Mejorar visibilidad y comenzar transición a ejecución real controlada.

## Prioridad 1 — Observabilidad (UI/Admin)
- Mostrar normalized_preview en admin
- Vista clara de:
  - provider
  - account_key
  - subject
  - recipients
  - thread_ref

## Prioridad 2 — Logging estructurado
- Añadir logs de:
  - draft creation
  - dispatch events
- Preparar base para auditoría

## Prioridad 3 — Provider real (solo draft)
- Integrar M365 draft API
- Mantener bloqueo de send

## Prioridad 4 — Refinamiento LLM (opcional)
- Permitir re-generación de drafts antes de ejecución

## No hacer aún
- No activar email.send
- No automatizar dispatch real
- No UI compleja

