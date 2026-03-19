# CHANGELOG

## 2026-03-19 — Opportunity Intelligence V2 refinement pass

### Added
- Human-readable semantic labels for prioritized opportunities:
  - priority labels
  - risk flag labels
  - next action labels
  - execution status labels
- Backend filters for prioritized opportunities UI:
  - high only
  - with autotasks
  - no action
  - with risk
- Visual badges in prioritized opportunities UI:
  - AUTO
  - BLOCKED
  - SUGGESTED
- Improved opportunity task detail UI:
  - AUTO / MANUAL source badges
  - human-readable task type labels
  - human-readable source action labels
  - execution summary block
  - risk / next action summary cards

### Changed
- Rebuilt `apps/opportunities/services/prioritization.py` as a complete, stable module after partial overwrite issue.
- `views_prioritized.py` now consumes enriched `row.to_dict()` payloads instead of relying on raw slugs in templates.
- `templates/opportunities/prioritized.html` now renders labels instead of internal slugs.
- `templates/opportunities/opportunity_tasks.html` now presents clearer operational governance semantics.

### Preserved / Verified
- Existing pipeline remains intact:

  `Email → Fact → Inference → Proposal → Recommendation → Task → Opportunity`

- Opportunity Intelligence V2 remains active:
  - scoring
  - priority buckets
  - risk flags
  - next actions
  - execution status
  - last_analyzed_at tracking
- Autotasking V1 remains operational:
  - threshold by priority
  - dedupe / reuse
  - source = auto/manual
  - source_action tracking

### Validation
- `python manage.py check` → OK
- `python manage.py runserver` → OK
- Prioritized UI validated on:
  - `/opportunities/prioritized/`
  - `?autotasks=1`
  - `?stage=new`
  - `?stage=qualified`
  - `?stage=proposal`
- `python manage.py analyze_open_opportunities` validated:
  - opportunities analyzed correctly
  - tasks reused correctly
  - monitor opportunities not auto-materialized below threshold

### Notes
This session focused on refinement, clarity, and control.
No architectural rebuild was performed.
