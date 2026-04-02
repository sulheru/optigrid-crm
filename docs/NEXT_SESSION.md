# NEXT SESSION — V2.7 Decision UI Integration

## Objetivo

Consumir Decision Output desde UI / Chat Console.

## Scope

- crear función:
  get_email_decision_view(email_id)

- integrar:
  build_decision_output(trace)

- renderizar:
  - selected rules
  - discarded rules
  - explanation
  - final effect

## Restricciones

- no modificar motor
- no modificar helpers
- no modificar explainability
- solo capa de consumo

## Criterio de éxito

- UI muestra decisión completa
- coherente con trace real
- útil para debugging humano
