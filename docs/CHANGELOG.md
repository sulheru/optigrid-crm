# OptiGrid CRM — Changelog

## 2026-03-12

### Added

Opportunity.source_recommendation field.

Permite trazabilidad directa entre AIRecommendation y Opportunity.

---

### Improved

Opportunity deduplication logic.

Antes:
title + summary

Ahora:
source_recommendation → fallback title + summary

---

### UI

Opportunity board ahora incluye:

- KPI metrics
- pipeline stage counts
- average confidence
- estimated pipeline value

---

### Stability

/opportunities/ endpoint validado y estabilizado.

Stage transitions funcionando correctamente.

---

### Architecture

Opportunity pipeline ahora completo:

Email → Facts → Inference → Proposal → Recommendation → Task → Opportunity

