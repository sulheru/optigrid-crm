# CHANGELOG — OptiGrid CRM

## [2026-03-19] — Governance Base (Tasks)

### Added
- Campo `is_revoked` en CRMTask
- Endpoint para revocar tasks desde UI
- Propiedades:
  - `is_auto`
  - `can_be_revoked`
  - `effective_status_label`

### Changed
- Refactor de modelo CRMTask:
  - Simplificación de task types
  - Nuevos estados: scheduled, blocked, cancelled
  - Eliminación de priority y source_recommendation

### Autotasker
- Añadido control de governance:
  - No recrear tasks si existe una revocada con mismo:
    - opportunity
    - source_action
- Filtro actualizado:
  - `_existing_task` ignora tasks revocadas

### Validated
- analyze_open_opportunities funcionando correctamente
- UI de tasks operativa
- Revocación persistente y respetada
- Sin regresiones en pipeline

### Result
Sistema autónomo con control humano efectivo (Human-in-the-loop v1)
