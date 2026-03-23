# NEXT SESSION — Cockpit V3

## 🎯 Goal

Introduce intelligence layer on top of recommendations:

👉 NEXT BEST ACTION ENGINE

---

## 🔥 Objectives

### 1. Next Best Action (NBA)
- Select single most important recommendation
- Based on:
  - priority_score
  - confidence
  - urgency signals
  - type weighting

### 2. Urgency Layer
- Detect time-sensitive actions
- Introduce:
  - urgency_score
  - overdue logic
  - escalation flags

### 3. Dashboard Upgrade
- New top block:
  → "What should you do now"
- Separate from list

### 4. Recommendation Ranking Engine
- Global scoring formula
- Sort across types

---

## 🧠 Key Idea

Move from:

List of actions → Decision system

---

## ⚙️ Suggested Implementation

- New module:
  apps.recommendations.engine

- Functions:
  - compute_priority()
  - compute_urgency()
  - get_next_best_action()

---

## 📌 Expected Outcome

System starts behaving like:

👉 Autonomous commercial brain

Not just assistant

