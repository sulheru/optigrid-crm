# NEXT SESSION

Project: OptiGrid CRM
Phase: Recommendation Operations Layer

## Goal

Transform recommendations into actionable CRM decisions from the UI.

## Tasks

1. Improve /recommendations/ view

Add:

- filters
- status indicators
- clearer recommendation types

2. Add actions

Buttons:

- Create Task
- Dismiss Recommendation
- Promote to Opportunity

3. Add state transitions

Recommendation states:

new
materialized
dismissed
executed

4. Add audit command

New management command:

python manage.py crm_pipeline_report

Outputs counts for:

emails
facts
inferences
recommendations
tasks
opportunities

5. Optional

Opportunity detail page
Task detail page
