# Next Session — Opportunity Intelligence Expansion

Current system supports:

python manage.py analyze_opportunity <id>

Next improvements:

## 1 Batch Opportunity Analysis

Add command:

python manage.py analyze_open_opportunities

Behavior:

- iterate over open opportunities
- run analysis
- generate recommendations

## 2 UI Integration

Opportunity list should display:

- recommendation count
- opportunity stage
- last analysis status

Opportunity detail page should show:

Opportunity Intelligence panel:

Context:

- key inference
- detected signals
- relevant email snippet

Recommendations:

- followup
- risk_flag
- next_action

## 3 Recommendation Materialization

Allow specific opportunity recommendations to become tasks.

Example:

followup → CRMTask

But only via explicit user action.

## 4 Observability

Add command:

python manage.py crm_pipeline_report

Include opportunity metrics:

- opportunities analyzed
- recommendations generated
- reuse ratio

Goal:

Visibility into Opportunity Intelligence effectiveness.
