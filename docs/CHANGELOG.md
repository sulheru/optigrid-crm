# CHANGELOG

## 2026-04-02 — CRM Update Engine V2.7 / V2.7.1 / V2.7.2

### V2.7 — Decision UI Integration
- Added `get_email_decision_view(email_id)` as UI-facing decision reader.
- Added `email_decision_detail` view and route for decision inspection.
- Added decision-detail navigation from inbox cards.
- Refactored `templates/emailing/decision_detail.html` to render:
  - selected rules
  - discarded rules
  - final effect
  - explanation
- Added dedicated tests for:
  - decision detail render
  - empty state
  - 404 behavior
  - inbox link visibility

### V2.7.1 — Decision Persistence Alignment
- Confirmed `RuleEvaluationLog` as source of rule trace persistence.
- Refactored trace lookup to use `source_type="inbound_email"` and `source_id=str(email.id)`.
- Confirmed `InboundDecision` uses `inbound_email` and `payload_json`.
- Refactored decision view consumption to prefer persisted decision data and fallback to rule logs.

### V2.7.2 — Semantic Final Effect
- Extended `final_effect` trace event with `semantic_effect`.
- Preserved compatibility with existing `final_effect=True` behavior.
- Added semantic fields:
  - `rule`
  - `proposal_type`
  - `payload`
  - `priority`
  - `outcome`
  - `is_final`
- Updated inbound decision derivation to use semantic effect as primary source.
- Reduced dependence on downstream heuristics for action type inference.
- Verified tests remain green across:
  - `apps.updates`
  - `apps.updates.test_decision_output`
  - `apps.emailing.tests_crm_update_engine`

### Inbox UI work completed this session
- Refactored `templates/emailing/decision_detail.html` to show:
  - persisted operational decision
  - semantic effect
  - explanation
  - selected/discarded rules
- Refactored `templates/emailing/partials/inbox_decision_panel.html` to display:
  - action type
  - status
  - priority
  - score
  - approval requirement
  - automation reason
  - semantic effect summary
  - top explanation lines
  - risk flags

### Known remaining work
- `inbox_decision_panel.html` exists but inbox integration still needs final wiring review.
- `inbox_view` currently hydrates decision state manually in Python; this should be cleaned up and optimized.
- Potential N+1 / view-template coupling still needs final cleanup in inbox rendering path.
