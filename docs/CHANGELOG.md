# CHANGELOG — OptiGrid CRM

## [Cockpit V2] — AI Recommendations UX & Execution Layer

### ✨ Added
- AI Recommended Actions panel fully integrated into Dashboard
- Unified execute endpoint:
  - /recommendations/<id>/execute/
  - Supports followup, contact_strategy, reply_strategy
- Dynamic available_actions system
- Semantic UI mapping via ui_semantics.py

### 🔧 Refactored
- recommendations/views.py cleanup
  - Removed duplicated logic
  - Standardized action handling
- dashboard_views.py
  - Centralized recommendation fetching
  - Introduced get_dashboard_data()

### 🎨 UI Improvements
- Replaced table layout with card-based design in recommendations
- Improved readability and hierarchy
- Consistent spacing, badges and actions
- Responsive layout fixes

### 🧠 System Behavior
- Recommendations now:
  - Have status lifecycle: new → executed / dismissed
  - Are deduplicated
  - Can trigger real actions (email drafts, tasks, etc.)

### 🐛 Fixed
- Import issues (apps.ai_recommendations)
- Broken dashboard rendering
- Inconsistent template references
- Action execution inconsistencies

---

## Current State

System behaves as:

AI → Recommendation → Execute → Action → CRM Update

User role:
Supervisor / CEO

System role:
Autonomous commercial operator (guided)

