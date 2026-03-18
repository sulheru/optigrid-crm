# NEXT_SESSION.md

## Estado al inicio de la próxima sesión
El sistema ya dispone de:
- pipeline CRM funcional
- Opportunity Intelligence V2
- UI de oportunidades priorizadas
- Autotasking V1 con feature flag
- vista de detalle de tasks por oportunidad

## Objetivo principal de la próxima sesión
Cerrar y pulir la capa Opportunity Intelligence + Autotasking antes de abrir nuevas superficies.

## Prioridades recomendadas

### 1. Pulido semántico y UX
Objetivo:
hacer que la UI y la lógica hablen el mismo idioma.

Tareas:
- reemplazar slugs técnicos visibles por labels legibles
  - `auto_task_open` → `Auto task open`
  - `define_next_action` → `Define next action`
  - etc.
- revisar mapping acción → task_type
  - `advance_opportunity` debería mapear a `opportunity_review`
  - `define_next_action` debería mapear a `review_manually`
  - `schedule_followup` debería mantener `follow_up`
- mejorar badges y copy de la UI priorizada

### 2. Validación real de Celery
Objetivo:
dar por cerrada la automatización periódica.

Tareas:
- levantar worker
- levantar beat
- validar que la task periódica dispara correctamente
- comprobar que respeta `AUTO_TASKING_ENABLED`
- comprobar que respeta batch size y ventana de reanálisis

### 3. Revisión de migraciones y consistencia
Objetivo:
asegurar que el estado del repo es limpio y coherente.

Tareas:
- revisar migraciones generadas en `opportunities` y `tasks`
- comprobar que no se sobreescribieron campos previos por accidente
- validar `python manage.py check`
- validar `python manage.py migrate`
- validar una segunda ejecución de análisis para confirmar reuse de autotasks

### 4. Pulido de trazabilidad operativa
Objetivo:
mejorar lectura y control de lo creado automáticamente.

Tareas:
- mostrar mejor `source_action` en UI
- mostrar enlace o relación clara task ↔ opportunity ↔ recommendation si aplica
- añadir filtros en vista priorizada:
  - solo auto tasks
  - solo blocked
  - solo suggested

## Objetivo secundario opcional
Solo si todo lo anterior queda limpio:
- añadir tests mínimos para Opportunity Intelligence y Autotasking
- al menos uno para dedupe de recomendaciones
- al menos uno para dedupe de autotasks

## No hacer todavía
- no abrir nuevos módulos grandes
- no introducir agentes más complejos
- no añadir demasiada automatización irreversible
- no mover demasiadas rutas o refactors cosméticos grandes

## Resultado esperado de la próxima sesión
Dejar cerrada una versión estable y más gobernable de:
- Opportunity Intelligence V2
- Prioritized Opportunities UI
- Autotasking V1

con semántica más clara, automatización periódica validada y repo listo para seguir evolucionando.

## Prompt sugerido para arrancar
Ver archivo `PROMPT_NEXT_SESSION.md` generado al cierre de esta sesión.
