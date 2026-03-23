# HANDOFF — CURRENT STATE

## System: OptiGrid CRM

### 🧩 Architecture

1. Communication Layer (Email)
2. CRM Core
3. Semantic Engine (LLM)
4. Governance Layer
5. Cockpit UI

---

## 🔁 Pipeline

Email → Fact → Inference → Proposal → Recommendation → Execute → Action

---

## ⚙️ Current Capabilities

### Recommendations
- Generated automatically
- Prioritized (priority_score, confidence)
- Executable via UI
- Status lifecycle:
  - new
  - executed
  - dismissed

### Execution
- Unified endpoint
- Action types:
  - followup
  - contact_strategy
  - reply_strategy

### Dashboard
- AI Recommended Actions block
- Sorted by priority/confidence
- Partial semantic mapping

---

## 🎨 UI

### Recommendations View
- Card-based layout
- Inline actions
- Clean hierarchy
- No table artifacts

---

## ⚠️ Known Gaps

- No global prioritization (Next Best Action)
- No urgency system
- No activity feed
- No cross-recommendation reasoning

---

## 🧠 System Nature

Transitioning from:
CRM → AI Operating System

User role:
Supervisor

