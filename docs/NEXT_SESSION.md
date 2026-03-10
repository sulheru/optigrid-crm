# OptiGrid CRM — NEXT SESSION

## Goal

Improve the **Opportunity Operations Layer** and reduce manual review workload.

## Priority Tasks

### 1 — Opportunity Pipeline UX

Improve `/opportunities/`:

Add:

- filters by stage
- sorting by estimated_value
- sorting by confidence

Optional:

- stage transition buttons

Example:

New → Qualified → Proposal → Won/Lost

This will turn the page into a real sales pipeline view.

---

### 2 — Task Specialization

Current report:

review_manually tasks: 26

We should reduce manual review.

Split task types:

- opportunity_review
- qualification_review
- pricing_review

Goal:

Reduce operational ambiguity.

---

### 3 — Recommendation Intelligence

Improve detection of opportunity signals.

Signals to detect:

- pricing discussion
- proposal request
- call scheduling
- scope discussion

Generate:

AIRecommendation(type="opportunity_review")

---

### 4 — Opportunity Enrichment

Automatically populate:

company_name
estimated_value
confidence

Sources:

- email metadata
- inference payload
- proposal content

---

### 5 — Pipeline Metrics

Extend `crm_pipeline_report`:

Add:

- average confidence
- opportunities created per recommendation type
- task completion rate

---

## Strategic Direction

Continue evolving OptiGrid CRM into a:

AI-driven **Opportunity Intelligence Engine**.

