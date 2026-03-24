# CHANGELOG — OptiGrid CRM

---

## 2026-03-24 — Provider Abstraction + Governance + Runtime

### ✨ Added

- Provider Abstraction Layer
  - MailProvider (embedded, m365)
  - LLMProvider (embedded, gemini)
  - registry desacoplado

- LLM structured output
  - JSON contract
  - normalization
  - validation

- Governance Layer V1
  - modo
  - confidence threshold
  - allowlist de tipos

- Runtime Settings
  - persistencia en DB
  - override dinámico de providers

---

### 🔧 Changed

- LLM integrado en inference pipeline
- providers desacoplados de lógica
- execution permanece intacta

---

### 🔒 Security / Safety

- HARD RULE:
  - prohibido envío automático de emails
  - solo drafts permitidos

---

### 🧠 Architecture

- transición a sistema IA-first gobernado
- adopción de modelo híbrido (Rules + LLM)

---

