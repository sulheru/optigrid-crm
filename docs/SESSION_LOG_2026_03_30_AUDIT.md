# SESSION LOG — Django Core Audit & Identity Cleanup

## Tipo de sesión
Auditoría técnica + intervención de emergencia

## Motivación

Errores en migraciones relacionados con referencias a:
- identity.Identity
- identity.Corporation
- identity.CorporateDomain

Sospecha adicional:
- posible corrupción del motor Django tras manage.py vacío en sesiones previas

---

## Diagnóstico

1. Django NO estaba corrupto
   - settings.py correcto
   - urls.py correcto
   - wsgi/asgi correctos
   - INSTALLED_APPS consistente

2. Problema real:
   - Referencias a app inexistente: identity
   - Intento fallido de refactor creando:
     - MailboxAccount duplicado en emailing
     - servicios dependientes de identity no existente

3. Confusión clave:
   - MailboxAccount ya existe en apps.tenancy.models
   - No debía redefinirse en emailing

---

## Intervención

- Eliminado MailboxAccount duplicado en emailing
- Eliminado servicio:
  apps/emailing/services/mailbox_identity.py
- Eliminadas referencias a identity
- Limpieza de residuos de migraciones
- Verificación completa del sistema

---

## Validación

python manage.py check → OK

Sistema estable

---

## Decisiones arquitectónicas

1. NO restaurar todo el proyecto
2. NO recrear identity aún
3. MailboxAccount canónico:
   → apps.tenancy.models

4. Identity Layer debe:
   - extender tenancy
   - no duplicar entidades

---

## Estado final

Sistema limpio, consistente y estable.

Listo para implementar correctamente:

Identity & Corporation Layer V1

---

## Aprendizaje clave

El problema no era técnico profundo sino:

→ incoherencia entre modelo mental y modelo real del sistema

