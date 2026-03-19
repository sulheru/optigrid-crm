# NEXT_SESSION

## Project
OptiGrid CRM — IA-First CRM System

## Starting point
System is stable after Opportunity Intelligence V2 refinement.

Already working:
- pipeline end-to-end
- Opportunity Intelligence V2
- Prioritized Opportunities UI
- Autotasking V1
- semantic presentation layer
- operational filters
- task detail governance-oriented UI

## Objective for next session
Implement the first Governance V3 capability:

# Revoke autotask + avoid automatic recreation

## Why this is next
The system can already:
- analyze
- prioritize
- suggest
- auto-create tasks under conditions

The missing control is:
- human revocation of an autotask
- protection against re-creation after revocation

Without this, the system executes partially but is not yet properly governed.

## Target outcome
Move from:

“system that analyzes, decides and executes partially”

to:

“system that analyzes, decides, executes partially, and can be explicitly overridden by humans”

## Minimum implementation scope

### 1. Task governance data
Prepare a way to record revoked autotasks.

Possible options:
- add `is_revoked`
- or add a dedicated status for revoked auto tasks
- or add a governance marker entity

Keep it minimal and consistent with current architecture.

### 2. Prevent recreation
Update autotasking logic so a revoked autotask is not recreated automatically for the same:
- opportunity
- source_action
- task_type

This is the most important behavior.

### 3. UI action
Add a revoke action for auto-created tasks from the opportunity task detail page.

Constraints:
- only for auto tasks
- safe and explicit
- no effect on manual tasks

### 4. Traceability
Preserve operational traceability:
- source
- source_action
- revoked state / marker
- audit-friendly behavior

## Constraints
- DO NOT break existing pipeline
- DO NOT duplicate decision logic
- DO NOT over-engineer governance yet
- DO NOT implement full approval workflow yet

## Recommended implementation order
1. inspect current `CRMTask` model
2. add minimal governance field/state
3. add revoke flow
4. protect autotasker from recreation
5. expose revoke control in UI
6. validate with repeated `analyze_open_opportunities`

## Validation checklist
Run:

```bash
cd ~/OptiGrid_Project/og_pilot/optigrid_crm
source .venv/bin/activate

python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py analyze_open_opportunities
python manage.py runserver

Then verify:

revoke existing autotask

rerun analyzer

confirm revoked autotask is not recreated

confirm manual tasks are unaffected

Files likely involved

apps/tasks/models.py

apps/opportunities/services/autotasker.py

apps/opportunities/views_prioritized.py or dedicated revoke view

apps/opportunities/urls.py

templates/opportunities/opportunity_tasks.html

Secondary optional stretch goal

If time remains:

add recommendation-origin link from task/opportunity detail

or add lightweight “decision reason” field for future auditability
