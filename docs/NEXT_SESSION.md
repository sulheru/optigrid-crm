# NEXT SESSION

## Objective
Finalize inbox integration for the upgraded Decision Engine UI.

## Context
The system already has:
- deterministic rule engine
- structured trace
- explainability
- decision output
- semantic final effect
- persisted `InboundDecision`
- detailed decision page
- upgraded inbox decision panel partial

What is still incomplete is the final inbox rendering cleanup.

## Scope
Focus only on inbox integration and rendering hygiene.

### Tasks
1. Review `apps/emailing/views.py::inbox_view`
   - clarify hydration of `suggested_decision`
   - clarify hydration of `latest_decision`
   - reduce ad hoc looping if possible
   - keep behavior deterministic

2. Review `templates/emailing/inbox.html`
   - confirm composition path
   - ensure decision panel is actually rendered in final layout

3. Review `templates/emailing/partials/inbox_email_card.html`
   - integrate decision panel cleanly
   - avoid duplicated decision rendering blocks
   - keep the card readable and compact

4. Review `templates/emailing/partials/inbox_decision_panel.html`
   - confirm it receives the correct object shape
   - confirm semantic effect summary renders safely

5. Validate no template-level ORM logic is reintroduced
   - no query-driven logic in template
   - view prepares all required data

## Constraints
- do not modify the rule engine unless strictly necessary
- do not modify explainability logic
- do not modify decision output format unless a rendering bug forces it
- avoid broad UI redesign
- prioritize clean wiring over visual embellishment

## Success criteria
- inbox renders decision panel consistently
- no duplicated decision sections inside inbox cards
- latest decision data is shaped in the view, not inferred in templates
- semantic effect is visible from inbox without opening detail page
- tests and `manage.py check` remain green

## If scope completes early
Next priority:
- begin Decision -> Action UI closure
  - apply
  - dismiss
  - decision state feedback
  - automation visibility
