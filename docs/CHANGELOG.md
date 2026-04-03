# CHANGELOG

## 2026-04-03 — IMPLEMENTATION — Decision Detail state contract repaired

Se corrige la interpretación semántica del estado en `Decision Detail`.

### Problema
La UI estaba tratando como decisión real un `decision_output` que solo contenía `explanation`, sin evidencia estructural de reglas o efecto final.

### Cambio aplicado
Se refactoriza la normalización de contexto y el render para distinguir correctamente entre:
- decisión real
- decisión operativa sin trace enriquecido
- ausencia de decisión

### Resultado
`apps.emailing.test_decision_detail` queda en verde.

---

## 2026-04-03 — IMPLEMENTATION — Decision Detail template aligned with backend state

Se ajusta `templates/emailing/decision_detail.html` para depender del estado semántico decidido por backend, en lugar de truthiness ambigua de payloads parciales.

---

## 2026-04-03 — IMPLEMENTATION — Views decision normalization hardened

Se refactoriza `apps/emailing/views_decision.py` para tratar como `decision_output` significativo solo aquel que contiene al menos una de estas evidencias:
- `selected_rules`
- `discarded_rules`
- `final_effect`

`explanation` queda explícitamente fuera del criterio de decisión real.

---

## 2026-04-03 — DOCUMENTATION — Next phase changed from implementation to audit

Tras cerrar `Decision Detail Trace Recovery`, la siguiente fase recomendada pasa a ser una auditoría técnica de madurez del proyecto.
