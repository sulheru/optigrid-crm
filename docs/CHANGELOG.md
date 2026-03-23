# CHANGELOG

## 2026-03-23 — Auditoría global y reorientación del roadmap

### Hecho en esta sesión
- auditoría estructural del sistema a partir de:
  - árbol real del proyecto
  - rutas activas
  - vistas principales
  - modelos clave
  - servicios de recommendations
  - services pipeline
  - emailing
  - tasks
  - opportunities
  - strategy
  - base.html y templates principales
- identificación del estado real del backend
- confirmación de que el sistema ya posee:
  - recommendation model operativo
  - execution layer funcional
  - ranking / urgency / decision-quality / NBA parcialmente implementados
  - pipeline facts/inferences/proposals
  - inbox intelligence paralela
  - simulación de correo activa
  - backend estratégico rule-based / Gemini parcial
- confirmación de que el cerebro del sistema existe, pero todavía no está completamente conectado ni gobernado como backend canónico

### Decisiones tomadas
- NO empezar todavía por integración completa Outlook / Graph
- NO empezar todavía por plugin completo de Calendar
- NO empezar todavía por SOI implementado de forma integral
- SÍ reorientar el roadmap hacia backend-first
- SÍ introducir una fase previa de consolidación:
  - canonical backend
  - provider abstraction
  - separación core vs adapters
- SÍ reconocer formalmente la idea de SOI como nueva capa futura de orquestación de escenarios
- SÍ considerar Calendar también como canal útil de notificaciones móviles, no solo agenda

### Nueva dirección
Nuevo roadmap backend-first:

1. CONTROL Y CANONICAL BACKEND
2. PROVIDER ABSTRACTION LAYER
3. SCENARIO ORCHESTRATOR INTERFACE (SOI)
4. REAL INTEGRATIONS
5. EXECUTIVE SURFACES

### Riesgo mitigado
Se evita conectar integraciones externas sobre un backend todavía ambiguo o mezclado.

