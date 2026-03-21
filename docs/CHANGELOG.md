# CHANGELOG

## 2026-03-21 — Automation Layer V3 + Supervisor UX

### Added
- `InboundDecision` extendido con:
  - `score`
  - `priority`
  - `risk_flags`
  - `applied_automatically`
  - `automation_reason`
- migración `0008_inbounddecision_automation_fields`
- servicio `decision_automation.py`
- scoring heurístico de decisiones inbound
- auto-apply seguro para decisiones permitidas
- policy basada en:
  - threshold
  - blocked actions
  - blocked risk flags
- settings de automatización:
  - `INBOX_AUTO_APPLY_ENABLED`
  - `INBOX_AUTO_APPLY_SCORE_THRESHOLD`
  - `INBOX_AUTO_BLOCKED_ACTIONS`
  - `INBOX_AUTO_BLOCK_ON_RISK_FLAGS`

### Improved
- `analyze_inbound_email()` ahora:
  - calcula score
  - asigna priority
  - genera risk flags
  - intenta auto-apply
- `apply_inbound_decision()` soporta aplicación automática auditada
- dedupe lógico de decisiones por inbound + action existente
- Inbox UI modernizada con:
  - score
  - priority
  - risk flags
  - automation reason
  - applied automatically
- Tasks UI modernizada con:
  - filtros
  - badges
  - revocation visibility
- Inbox supervisor filters:
  - decision status
  - auto/manual
  - priority
  - with/without risk

### Fixed
- conflicto de resolución de templates:
  - Django estaba usando `templates/...` en vez de `apps/.../templates/...`
- alineación de template raíz para Inbox
- modernización de template raíz para Tasks

### Validated
- migración aplicada correctamente
- tests de `apps.emailing` pasando
- auto-apply validado desde navegador
- casos manuales bloqueados correctamente
- no duplicación validada en flujo observado

### Result
Sistema pasa de:
AI-assisted CRM  
→ AI-driven commercial loop supervisable  
→ Semi-autonomous commercial agent foundation
