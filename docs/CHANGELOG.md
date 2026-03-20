# CHANGELOG

## 2026-03-20 — Inbox Intelligence V1 + System Stabilization

### 🧠 Inbox Intelligence V1 (NEW)

- Añadido `InboundInterpretation`
- Añadido `InboundDecision`
- Servicio `analyze_inbound_email` integrado en inbox_view
- Interpretación automática en tiempo de lectura (lazy execution)
- UI actualizada con:
  - intent
  - urgency
  - sentiment
  - confidence
  - recommended_action
  - rationale
  - signals
  - suggested decision

### 📥 Inbox UI

- Panel de inteligencia IA añadido por email
- Visualización clara de decisiones sugeridas
- Mantiene control humano (no auto-apply aún)

### 📤 Outbox

- Sin cambios funcionales
- Base estable para follow-ups desde inbound

### 🧠 Opportunities

- Fix completo de `context_builder`
- Eliminada dependencia de modelo legacy `EmailMessage`
- Integración con:
  - OutboundEmail
  - InboundEmail

### 🧭 Routing / URLs

- Eliminado namespace inconsistente `opportunities_ui`
- Corrección de templates:
  - prioritized.html
  - opportunity_tasks.html

### 🏠 Dashboard

- Restaurado `/` con TemplateView (mock estable)

### 🧪 Tests

- Tests emailing OK
- Sistema sin errores runtime

---

## Estado general

Sistema estable ✅  
Pipeline completo operativo ✅  
Inbox Intelligence V1 activo ✅  

