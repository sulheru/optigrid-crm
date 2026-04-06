# OptiGrid CRM — Master Architecture & Refactor Objective Document

## 1. Context

This project is an AI-first CRM platform designed to operate through a deterministic core, governed execution boundaries, and an AI orchestration layer (Sofía).

The current system is functionally advanced but suffers from architectural coupling:
- Refactors break unrelated components
- Responsibilities are mixed across layers
- External effects are not strictly controlled
- AI logic is not properly isolated

---

## 2. Core Objective

Refactor the system into a **layered, black-box architecture** where:

- Each layer has strictly defined responsibilities
- Each layer only communicates with allowed layers
- Failures are contained within layers
- No layer can bypass critical system boundaries

---

## 3. Architectural Principles

### 3.1 Black Box Principle
Each layer must behave as an isolated system:
- Defined inputs
- Defined outputs
- No internal leakage

### 3.2 Boundary Enforcement
Two critical system boundaries must never be bypassed:
- **Update Boundary** → all internal state changes
- **Execution Boundary** → all external side effects

### 3.3 Separation of Concerns
Strict separation between:
- Input normalization (EIL)
- Business logic (Application)
- Orchestration (Sofía)
- Domain definition (Core)

### 3.4 Determinism First
- Core and rule engine must remain deterministic
- AI is assistive, not authoritative over domain truth

### 3.5 Human-in-the-loop for Irreversible Actions
- External actions require approval unless explicitly allowed

---

## 4. Layered Architecture Definition

### Core Layer
Defines entities, states, events, invariants.
No external calls.

### Application Layer
Handles use cases and business logic.
Cannot execute external actions.

### Sofia Orchestration Layer
Central AI orchestrator.
Routes workflows and builds context.

### Access Layer
UI, API, chat, authentication.
No business logic.

### EIL
Normalizes external inputs.
No decisions or state changes.

### I/O Hooks
External integrations.
No domain logic.

### Plugins
Extend capabilities.
Cannot alter core rules.

### Event Bus
Event propagation and traceability.

### Workflows
Reactive processes triggered by events.

### Update Boundary
Applies internal changes.

### Execution Boundary
Executes external actions safely.

---

## 5. Dependency Rules

- Core → no dependencies
- Application → Core
- Sofía → Application
- Access → Sofía/Application
- Workflows → Event Bus + Application
- Boundaries → Core + Policies

---

## 6. Refactor Strategy

1. Define architecture
2. Identify violations
3. Introduce boundaries
4. Isolate I/O
5. Extract workflows
6. Clean application layer
7. Introduce Sofía
8. Reroute access
9. Harden system

---

## 7. Final Goal

A modular, stable, AI-orchestrated CRM where:
- Refactors are safe
- Behavior is traceable
- AI is controlled
- Side effects are safe

---

## 8. Key Insight

The goal is not to refactor code.
The goal is to refactor **system boundaries**.
