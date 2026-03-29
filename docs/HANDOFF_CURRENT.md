# HANDOFF — CURRENT STATE

## Estado general
El sistema OptiGrid CRM ha completado la integración del Mail Provider Layer en el flujo real de ejecución.

## Capacidades activas

### Knowledge
- Modelos estabilizados
- Tests en verde
- Migraciones coherentes

### Recommendations → External Actions
- Generación de intents automática desde recommendations
- Soporte para:
  - followup
  - reply_strategy
  - contact_strategy

### Mail Provider Layer
- Payload provider-aware
- Multi-account ready
- Thread-aware

### Resolución dinámica
- account_key heredado desde:
  - recommendation
  - metadata
  - inbound_email
  - thread
- thread_ref heredado desde inbound

### Observabilidad
- normalized_preview implementado
- incluye:
  - provider
  - account_key
  - destinatarios
  - subject
  - thread_ref
  - provider_status

### Guardrails
- email.send bloqueado globalmente
- solo se generan drafts

## Flujo actual

Recommendation
→ ExternalActionIntent
→ Provider Context
→ Dispatcher (stub)

## Estado técnico
- Tests globales: OK
- Sin errores en runtime
- Sistema estable

## Limitaciones actuales
- Provider real no conectado (stub)
- UI no muestra aún normalized_preview
- Resolución inbound basada en heurísticas

