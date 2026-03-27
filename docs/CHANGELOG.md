# CHANGELOG

## 2026-03-26 — External Actions Stabilization

### FIXES CRÍTICOS

- Eliminada recursión en dispatcher
- Eliminado auto-dispatch en creación de intents
- Corrección de estados (READY_TO_EXECUTE vs SUCCEEDED)
- Restauración de idempotencia en bridge
- Corrección de tests dependientes de modelo AIRecommendation

### MEJORAS

- Separación clara:
  - create_intent
  - dispatch_intent

- Introducción de patrón controlado de ejecución

### TESTING

- apps.external_actions: OK
- apps.recommendations: OK
- apps.emailing: OK

### DECISIONES ARQUITECTÓNICAS

- create_intent nunca ejecuta
- ejecución siempre explícita
- human approval por defecto

