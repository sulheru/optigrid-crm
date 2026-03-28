# SESSION LOG — 2026-03-28

## Objetivo

Estabilizar el CORE CONTROL LAYER antes de integrar:
- LLM real
- Mail real

## Trabajo realizado

1. Auditoría de creación de AIRecommendation
2. Eliminación de rutas paralelas
3. Introducción de factory central
4. Consolidación de execution layer
5. Integración completa de external actions
6. Restauración del inbound pipeline
7. Fix de compatibilidad inbound → execution

## Problemas encontrados

- Execution fallaba sin opportunity
- Drafts no se creaban
- Dedupe inconsistente
- Tests inbound rotos

## Resoluciones

- Cambio de scope a inbound_email
- Mapping explícito de acciones
- Resolución correcta de inbound/opportunity
- Compatibilidad con inbound_decision legacy

## Resultado

- Sistema estable
- Pipeline determinista
- Tests críticos en verde

## Pendiente

- Fix módulo knowledge (no crítico)
