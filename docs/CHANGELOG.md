# CHANGELOG — OptiGrid CRM

## 2026-03-18 — Opportunity Intelligence V1 (Batch Analysis)

### Added
- Nuevo comando: `analyze_open_opportunities`
- Servicio central: `analyze_opportunity_core`
- Generación automática de recomendaciones sobre oportunidades abiertas:
  - followup
  - next_action
  - risk_flag

### Improved
- Refactor de `analyze_opportunity` para usar lógica compartida
- Eliminación de duplicación de lógica de análisis

### Behavior
- Sistema ahora analiza oportunidades en batch
- Detección de señales desde contexto reconstruido
- Dedupe de recomendaciones existente

### Validated
- No duplicación de recomendaciones
- Reuse correcto en ejecuciones sucesivas
- Pipeline intacto (no rompe flujo existente)

### Notes
Primera versión del Opportunity Intelligence Layer operando de forma semiautomática.
