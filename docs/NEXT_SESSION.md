# NEXT SESSION

## Objetivo
Resolver la recuperación de `decision_output` y `trace` en `Decision Detail`.

## Foco exacto
Trabajar solo sobre:
- `apps/emailing/decision_detail.py`
- `apps/emailing/test_decision_detail.py`
- si hace falta, inspección puntual de:
  - `apps/updates/models.py`
  - `apps/emailing/models.py`
  - estructura real de `payload_json`
  - relación real con `RuleEvaluationLog`

## Meta funcional
Conseguir que `Decision Detail` muestre correctamente, cuando existan:
- Selected Rules
- Discarded Rules
- Explanation
- Semantic Effect

## Meta de tests
Dejar en verde:
- `python manage.py test apps.emailing.test_decision_detail`

## Plan recomendado
1. inspeccionar cómo están persistidos realmente:
   - `InboundDecision.payload_json`
   - `RuleEvaluationLog`
2. comparar eso con lo que `decision_detail.py` intenta leer
3. corregir la lógica de recuperación
4. solo después ajustar los tests si el contrato cambió realmente
5. volver a probar con curls sobre:
   - `/inbox/<id>/decision/`

## No hacer
- no volver a tocar inbox
- no abrir nuevas rutas
- no rediseñar la UI
- no tocar Rule Engine
- no tocar explainability
- no añadir persistencia nueva

## Comprobación final esperada
En al menos un caso con trace disponible, la vista debe renderizar:
- `Selected Rules`
- `Explanation`

Y en casos sin trace:
- mantener `Trace Not Available`
sin contradicción visual.
