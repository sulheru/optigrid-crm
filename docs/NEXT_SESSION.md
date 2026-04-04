# Next Session — Entity & Identity Layer (EIL)

## Objetivo

Diseñar la capa de entidades e identidad del sistema.

NO implementar.

## Problema a resolver

El sistema carece de:

- identidad
- ownership
- contexto organizativo
- modelo de usuarios

Esto bloquea:

- control de acceso
- multi-tenant real
- integraciones futuras (M365, SMTP)
- coherencia de datos

## Enfoque

Diseño desde el sistema, no desde el usuario.

Principio:

El sistema es email-driven, no login-driven.

## Alcance

Definir:

1. Modelo Organization (entidad)
2. Modelo User (actor)
3. Relación email → entidad
4. Ownership del CRM
5. Reglas de resolución de dominio
6. Flujo de creación automática

## Importante

NO incluir:

- login completo
- permisos complejos
- UI de usuarios
- OAuth / SSO

## Resultado esperado

- modelo claro y mínimo
- sin sobreingeniería
- listo para implementación progresiva
- compatible con inbound automático

