# HANDOFF — OptiGrid CRM

---

## 🧠 ESTADO ACTUAL

Sistema IA-first con backend canónico completamente consolidado.

Pipeline operativo:

Email → Fact → Inference → Recommendation → Execution

---

## 🧱 CAPAS IMPLEMENTADAS

### ✔ Core

- pipeline determinista funcionando
- execution desacoplada
- entrypoints únicos:
  - InferenceService
  - execute_recommendation_service

---

### ✔ Provider Abstraction Layer

- MailProvider
  - embedded
  - m365 (wrapper)

- LLMProvider
  - embedded
  - gemini (wrapper)

- registry desacoplado

---

### ✔ LLM Integration

- salida estructurada (JSON)
- normalización de tipos
- validación
- integración en inference

---

### ✔ Governance Layer V1

- control por:
  - modo (LLM_OUTPUT_MODE)
  - confianza
  - tipos permitidos

---

### ✔ Runtime Settings

- modelo persistente (DB)
- prioridad:
  DB > settings.py > default
- control dinámico:
  - MAIL_PROVIDER
  - LLM_PROVIDER

---

## 🔒 HARD RULE GLOBAL

NINGUNA IA puede enviar emails automáticamente.

- permitido:
  - create draft

- prohibido:
  - send email automático

El envío requiere acción humana explícita.

---

## 🧠 MODELO DE DECISIÓN

Modelo C:

Rules + LLM → (futuro: Merge Layer) → Governance → Execution

Estado actual:

- sistema híbrido
- rules activas
- LLM integrado
- merge aún no explícito

---

## ⚠️ LIMITACIONES ACTUALES

- no existe merge layer
- duplicidad potencial rules / LLM
- no hay explainability en UI
- Gemini aún no en uso real

---

## 🧭 SIGUIENTE PASO NATURAL

Recommendation Merge Layer V1

---

## 🧠 PRINCIPIO DEL SISTEMA

IA controla el sistema interno  
Humano controla efectos irreversibles

---

