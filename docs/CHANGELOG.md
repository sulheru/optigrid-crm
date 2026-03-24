# CHANGELOG

## 2026-03-24

### Added
- Canonical backend structure
- Execution layer split:
  - execution_application.py
  - execution_actions.py
  - execution_adapters.py
  - execution.py (facade)

### Changed
- Unified inference entrypoint
- Unified recommendation execution
- Inbox now routes through recommendations

### Fixed
- Duplicated inference generation
- Execution logic fragmentation
- Hidden side-effects in services

### Notes
- System ready for Provider Abstraction Layer
