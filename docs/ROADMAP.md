# ROADMAP

## Estado actual
### Fases cerradas
- Rule Engine determinista
- RULE_TRACE estructurado
- Explainability layer
- Decision Output layer
- Persistencia de trace y decisión operativa
- Inbox Decision Panel integrado
- Decision Detail Trace Recovery

### Último cierre relevante
Se corrige el contrato de estado de `Decision Detail`:
- explicación sola ya no implica decisión
- UI alineada con semántica real
- tests de `apps.emailing.test_decision_detail` en verde

## Próxima fase inmediata
### Auditoría técnica de madurez del sistema

Objetivo:
medir el estado real del proyecto y cuantificar la distancia a integraciones clave.

### Áreas a auditar
- input/inbox
- decision core
- state/UI contract
- execution/apply/send
- integration/provider layer

### Auditorías específicas
1. readiness de correo real:
   - SMTP
   - M365
   - SMLL
2. readiness de AI Studio / LLM:
   - agente interactor interno
   - agente escaneador de leads

### Entregable de cierre de fase
- mapa de madurez por capas
- bloqueos reales
- roadmap realista de implementación

## Fase posterior probable
### Email Integration Implementation Readiness
Solo después de la auditoría.

Se decidirá qué provider abordar primero:
- SMTP como vía más directa
- M365 como integración estructural objetivo
- SMLL según encaje real de arquitectura

## Fase posterior probable
### LLM Entry Boundary
Objetivo:
definir el punto correcto de entrada para AI Studio sin romper:
- determinismo
- trazabilidad
- separación entre inferencia y decisión

## Nota estratégica
La prioridad inmediata ya no es seguir refactorizando UI.
La prioridad inmediata es obtener una visión precisa del grado real de avance del sistema y del esfuerzo restante para providers de correo y LLM.
