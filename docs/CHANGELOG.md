# CHANGELOG

## 2026-04-03 — Inbox Decision Integration Cleanup + Decision Detail state cleanup

### Hecho
- Se estabilizó la integración del decision panel en inbox.
- Se limpió el script de fetch para usar solo rutas válidas.
- Se corrigieron roturas introducidas durante refactors intermedios en `views.py`.
- Se restauraron imports y views requeridas por `urls.py`.
- Se alineó `inbox_email_card.html` con los tests usando el label:
  - `View decision`
- Se mejoró la semántica de `Decision Detail`:
  - antes: podía mostrar decisión operativa y a la vez `Decision Not Available`
  - ahora: distingue correctamente el caso `Trace Not Available`

### Resultado visible
- `/inbox/` estable
- `/inbox/<id>/decision/` renderiza
- la decisión operativa persistida se muestra correctamente
- desaparece la contradicción visual previa entre decisión operativa y estado vacío total

### Pendiente
- `apps.emailing.test_decision_detail` no queda completamente verde
- `decision_detail.py` no reconstruye correctamente `decision_output` / `trace` para los casos reales probados
- no aparecen aún:
  - Selected Rules
  - Discarded Rules
  - Explanation
  - Semantic Effect
  en los casos donde deberían recuperarse desde persistencia o logs

### Nota
No se introdujo nueva persistencia.
No se modificó el Rule Engine.
No se modificó explainability.
No se introdujo LLM.
