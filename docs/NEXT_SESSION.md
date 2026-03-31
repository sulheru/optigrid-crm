# NEXT SESSION

## Objetivo principal
Implementar el entrypoint mínimo del CRM Update Engine para cerrar el loop del pipeline actual.

## Contexto real
- Tenancy/corporation layer estable
- Domain resolution implementado
- SMLL estable
- Provider layer reforzado
- Tests verdes
- `manage.py check` limpio

## Problema actual
El pipeline de emailing intenta llamar a:
- `apps.crm_update_engine.entrypoints.process_email`

pero el módulo no existe en la ruta esperada.

## Objetivo técnico concreto
Crear:
- `apps/crm_update_engine/entrypoints.py`

Con al menos:
- `process_email(email)`

## Requisitos
- no romper tests existentes
- no tocar providers reales
- no meter UI
- no meter envío automático
- mantener diseño IA-first
- mantener separación entre core y adaptadores

## Resultado esperado
- pipeline ya no cae en `ModuleNotFoundError`
- existe un entrypoint canónico para evolución futura
- queda preparado el siguiente paso:
  - persistir tenant/mailbox scope en emailing

## Ficheros previsibles a tocar
- `apps/crm_update_engine/entrypoints.py`
- posible `apps/crm_update_engine/__init__.py`
- posible wiring mínimo con servicios existentes

## Validación esperada
- `python manage.py test apps.tenancy apps.simulated_personas apps.emailing`
- `python manage.py check`
