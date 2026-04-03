# CHANGELOG

## 2026-04-03 — AUDIT — Provider/runtime/sidebar audited for plugin readiness

Se auditan los ficheros reales de:
- `config/settings.py`
- `apps/core/runtime_settings.py`
- `apps/emailing/services/mail_provider_service.py`
- `apps/emailing/services/provider_router.py`
- `apps/providers/*`
- `templates/base.html`
- `templates/partials/app_sidebar.html`

Hallazgos principales:
- existe base de runtime config y provider abstraction
- el sidebar sigue hardcodeado
- `M365` sigue siendo stub
- `embedded` sigue siendo stub funcional
- `provider_router` mantiene acoplamiento directo con SMLL
- mailbox / tenant aún no se persisten de forma canónica

---

## 2026-04-03 — DECISION — Plugin phase postponed until core operational closure

Se decide no iniciar todavía la fase de plugins de Sofía.

Motivo:
aunque el sistema ya está suficientemente maduro para pluginización arquitectónica, el core aún no está cerrado para operación real completa.

La nueva prioridad pasa a ser:
- cerrar identidad operativa canónica
- cerrar execution engine
- cerrar providers reales
- cerrar convergencia runtime/provider

---

## 2026-04-03 — STRATEGY — Core must be production-ready before Sofía OS

Se fija como criterio estratégico que el sistema debe quedar preparado para producción real antes de introducir:
- plugin manifests
- plugins fijos vs removibles
- sidebar dinámico por plugins
- lifecycle formal de plugins

---

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
