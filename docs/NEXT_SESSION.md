# NEXT SESSION — SMLL Integration V1

## Objetivo
Integrar el SMLL Engine dentro del sistema de emailing sin usar providers reales.

## Alcance

### 1. Simulated Email Adapter
- mapear EmailMessage → SimulatedIncomingMessage
- mapear SimulatedReplyResult → EmailMessage

### 2. Provider Hook

Condición:
email.provider == "mail_embedded"

Acción:
- usar SMLL engine
- evitar providers reales

### 3. Persistencia

- inbound simulated emails
- outbound simulated replies
- usar modelos existentes (no duplicar)

### 4. Flags

- marcar emails como:
  - simulated
  - source = smll

## Restricciones

- NO side effects externos
- NO envío real de correos
- mantener compatibilidad con pipeline existente

## Resultado esperado

Sistema capaz de:
- simular conversación completa
- alimentar pipeline CRM
- generar recomendaciones reales

