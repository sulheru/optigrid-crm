# HANDOFF

Project: OptiGrid CRM
Date: 2026-03-08

## Current State

The system now implements a full IA-first CRM pipeline.

Email processing pipeline:

EmailMessage
 → FactRecord
 → InferenceRecord
 → AIRecommendation
 → CRMTask
 → Opportunity

### UI

Dashboard:
/ 

Email inspection:
/emails/
/emails/<id>/

Operational views:
/recommendations/
/tasks/
/opportunities/

### Automation

Task materialization:

python manage.py materialize_recommendations

Opportunity promotion:

python manage.py promote_tasks

Both processes are idempotent.

### Key milestone

The system has moved from a passive inference engine to an operational CRM capable of generating tasks and opportunities.

## Next logical step

Enhance Recommendations UI:

- action buttons
- task creation from UI
- recommendation state transitions
