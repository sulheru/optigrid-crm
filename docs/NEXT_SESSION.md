# NEXT SESSION — OptiGrid CRM

---

## CONTEXTO

Sistema IA-first con:

- providers desacoplados
- LLM integrado
- governance operativa
- runtime settings activos

Modelo:

Rules + LLM (sin merge aún)

---

## OBJETIVO

Implementar:

Recommendation Merge Layer V1

---

## ALCANCE

1. Introducir source en Recommendation

- rules
- llm
- merged

---

2. Merge básico

- agrupar por type
- deduplicar
- priorizar rules como base

---

3. Integración

- conectar en pipeline antes de governance

---

## REGLAS

- NO romper execution
- NO refactor agresivo
- mantener backward compatibility
- NO introducir complejidad innecesaria

---

## RESULTADO ESPERADO

- una sola lista coherente de recommendations
- sin duplicados
- base preparada para explainability

---

