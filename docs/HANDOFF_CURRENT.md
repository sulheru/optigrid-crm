# HANDOFF — CRM Update Engine V2.6

## Estado actual

El sistema dispone ahora de una capa completa de decisión estructurada:

- RULE_TRACE estructurado (V2.3)
- Query helpers (V2.4)
- Explainability (V2.5)
- Decision Output Layer (V2.6)

## Nueva capacidad

Se ha introducido:

build_decision_output(trace)

Output:

{
  selected_rules: [{rule: str}],
  discarded_rules: [{rule: str}],
  final_effect: dict,
  explanation: List[str]
}

## Propósito

Unificar la salida del motor para:

- UI
- Chat Console
- debugging
- auditoría

## Arquitectura

RULE ENGINE → TRACE → HELPERS → EXPLAINABILITY → DECISION OUTPUT → UI

## Estado

- determinista
- desacoplado
- validado por tests
