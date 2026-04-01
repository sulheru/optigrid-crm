# Próxima sesión — CRM Update Engine V2.3

## Objetivo

Evolucionar RULE_TRACE hacia estructura más formal y explotable.

## Líneas de trabajo

1. Normalización del trace
   - Definir esquema estructurado (no dict libre)
   - Introducir tipos de evento (enum)

2. Preparación para consumo externo
   - Hacer trace legible por Chat Console
   - Soporte para explicación de decisiones

3. Mejora de debugging
   - Posibilidad de reconstruir decisión paso a paso
   - Preparar base para replay enriquecido

## Restricciones

- Mantener compatibilidad con logs actuales
- No introducir persistencia adicional
- No cambiar comportamiento del motor

