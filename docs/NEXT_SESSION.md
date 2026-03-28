# NEXT SESSION — MAIL PORT MULTI-ACCOUNT READY

## Objetivo

Diseñar e implementar el Mail Provider Layer.

## Requisitos

- Abstracción de proveedor (SMTP / Microsoft / etc)
- Soporte multi-cuenta
- Configuración dinámica (runtime settings)
- Integración con ExternalActionIntent

## Restricciones

- NO envío automático de emails
- Solo creación de drafts
- Dispatch debe seguir bloqueado

## Entregables

- mail_provider interface
- implementación dummy/provider base
- integración con execution_adapters
- settings configurables

## No incluir

- UI
- envío real
- autenticación compleja

## Validación

- Tests siguen en verde
- Drafts siguen funcionando
- External intents siguen generándose
