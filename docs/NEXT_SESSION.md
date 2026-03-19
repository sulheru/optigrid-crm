# NEXT SESSION — Conversation Intelligence V1

---

## 🎯 Objective

Convert inbound replies into structured decisions.

---

## 🧩 Tasks

### 1. Reply Interpretation Layer

Create service:

- interpret_reply(inbound)

Output:

- intent
- urgency
- recommended_action

---

### 2. Decision Engine

Map reply_type → actions:

- interested → create next step
- needs_info → generate detailed reply
- not_now → create follow-up task
- not_interested → mark opportunity inactive
- unclear → clarification reply

---

### 3. Opportunity Update

Enhance:

- stage transitions
- priority updates
- engagement scoring

---

### 4. UI Enhancements

- show "AI Suggested Action"
- one-click apply

---

## 🧠 Key Principle

From:

Inbox = messages

To:

Inbox = decisions

---

## ⚠️ Constraint

NO full automation yet.

Keep:

AI suggests → User approves

---

## 🚀 Stretch Goal

Auto-generate follow-ups without clicking "generate"
(but still require approval)

---

## 🧭 Expected Outcome

System becomes:

AI Sales Assistant → AI Sales Operator
