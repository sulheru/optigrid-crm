# Decision Output Layer

## Función

build_decision_output(trace)

## Propósito

Convertir trace interno en payload consumible por UI.

## Output

{
  selected_rules: [{rule: str}],
  discarded_rules: [{rule: str}],
  final_effect: dict,
  explanation: List[str]
}

## Notas

- NO evalúa reglas
- NO modifica trace
- SOLO adapta formato

## Arquitectura

Motor → Trace → Helpers → Output → UI
