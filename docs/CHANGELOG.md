# CHANGELOG

## [Session — Conversation Loop Completed]

### 🚀 Added

#### Outbox Improvements
- email_type separation (first_contact / followup)
- bulk actions (approve, send, draft)
- UI filters and controls

#### Inbox V1
- InboundEmail model
- reply_type classification (simulated)
- inbox view
- status tracking (new, reviewed, linked)

#### Inbound Simulation
- automatic reply generation after send
- deterministic pattern system

#### Follow-up Engine V1
- reply-based draft generation
- contextual messaging per reply_type
- inbound → outbound linking
- duplicate prevention

---

### 🧠 Architectural Shift

System evolved from:

Outbound automation

→ to:

Conversation loop system

---

### 🔥 Result

First working version of:

AI-driven commercial conversation engine
