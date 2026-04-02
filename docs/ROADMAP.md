# ROADMAP

## Current phase
Decision Engine consolidation and UI operationalization.

---

## Completed

### CRM Update Engine
- V2.0 rule-based core
- V2.1 declarative conditions
- V2.2 trace semantics refinement
- V2.3 structured trace and decision model
- V2.4 trace normalization and query helpers
- V2.5 explainability layer
- V2.6 decision output layer
- V2.7 decision UI integration
- V2.7.1 decision persistence alignment
- V2.7.2 semantic final effect

### Emailing / Inbox Intelligence
- inbound interpretation model
- inbound decision model
- decision apply / dismiss services
- decision detail view
- semantic effect visible in detail UI
- upgraded inbox decision panel partial

---

## In progress

### Inbox decision integration cleanup
Status: active

Pending:
- finalize decision panel wiring in inbox card composition
- simplify `inbox_view` data shaping
- reduce view/template coupling
- ensure clean latest-decision hydration path

---

## Next

### V2.8 — Decision Action UI Closure
Goal:
turn suggested decisions into a clean visible action workflow.

Expected scope:
- apply / dismiss state feedback in inbox
- visible execution state
- clearer automation visibility
- refined operational decision presentation

### V2.9 — Policy-aware execution
Goal:
make execution policy explicit and rule-compatible.

Expected scope:
- approval-aware routing
- blocked actions visibility
- action constraints by policy
- better automation reason surface

### V3.0 — Decision Console / Chat Console foundation
Goal:
make decision traces conversationally explorable.

Expected scope:
- trace narrative view
- semantic effect summary
- decision history thread
- human validation support

---

## Long-term direction
The product is evolving from a CRM with AI features into:

`Decision System with CRM surfaces`

Core principle:
- the rule engine remains the deterministic source of truth
- UI, automation, and future LLM layers consume that truth rather than inventing it
