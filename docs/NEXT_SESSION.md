# NEXT SESSION

## Objetivo
Realizar una auditoría técnica estructurada del estado real de OptiGrid CRM.

## Preguntas que debe responder la auditoría
1. ¿Cuán avanzado está realmente el proyecto?
2. ¿Qué está terminado, qué está parcial y qué falta?
3. ¿A qué distancia estamos de implementar correo real mediante:
   - SMTP
   - Microsoft 365
   - SMLL
4. ¿A qué distancia estamos de integrar AI Studio como:
   - agente interactor del sistema vía LLM
   - agente escaneador de leads en la red?

## Capas a evaluar
- Input layer
- Decision layer
- State layer
- Execution layer
- Integration layer

## Ficheros prioritarios para inspección
- `apps/emailing/views.py`
- `apps/emailing/views_decision.py`
- `apps/emailing/models.py`
- `apps/emailing/services/mail_provider_service.py`
- `apps/emailing/services/provider_router.py`
- `apps/emailing/services/outbound_sender.py`
- `apps/emailing/services/inbound_analysis_service.py`
- `apps/emailing/services/inbound_decision_engine.py`
- `apps/emailing/services/inbound_decision_apply_service.py`
- `apps/emailing/services/inbound_decision_from_trace.py`
- `apps/emailing/services/inbound_interpreter.py`
- `apps/emailing/services/recommendation_bridge.py`
- `apps/updates/services.py`
- `apps/updates/decision_output.py`
- `apps/updates/explainability.py`
- configuración de settings relevante para providers

## Entregables esperados
1. matriz de madurez por área
2. readiness SMTP / M365 / SMLL
3. readiness AI Studio / LLM
4. bloqueos técnicos reales
5. roadmap realista corto y medio plazo

## No hacer
- no implementar aún SMTP
- no implementar aún M365
- no meter aún LLM
- no reabrir refactors de Decision Detail salvo que la auditoría detecte bloqueo estructural

## Criterio de éxito
Terminar la sesión con una visión clara, basada en código real, de:
- estado actual
- huecos críticos
- prioridad de integraciones
- punto correcto de entrada para LLM
