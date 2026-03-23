# CHANGELOG — OptiGrid CRM

## 2026-03-23 — UI Foundation V2 Consolidation (Partial)

### Added
- Consolidated `design_system.html` with reusable UI components:
  - buttons, badges, forms, tables, layout helpers, chat components
- Unified visual language across:
  - Tasks
  - Leads
  - Opportunities
  - Strategic Chat

### Changed
- Refactor of legacy templates to use `app-*` design system
- Removal of multiple inline styles (partial)
- Alignment with app shell (sidebar + topbar)

### In Progress
- `base.html` cleanup (separation of shell vs design system)
- Full removal of duplicated styles

### Pending
- Final UI polish (remove remaining inline styles)
- Full system audit (next session)
- Validation of template consistency across all views
