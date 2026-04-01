
## [V2.2] — Trace Semantics Refinement

### Added
- Explicit trace fields:
  - condition_match
  - rule_selected
  - rule_discarded
  - discard_reason
- final_effect trace entry

### Fixed
- Final rule now correctly stops further rule selection
- Prevented fallback rules from being selected after final rule

### Notes
- No functional changes to rule evaluation output
- Full backward compatibility preserved
- Replay and diff remain unaffected

