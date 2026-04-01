from typing import Any, Dict


def evaluate_condition(condition: Any, context: Dict) -> bool:
    """
    Soporta:
    - dict declarativo
    - callable legacy
    - None / vacío de forma segura
    """

    if condition is None:
        return False

    # Compatibilidad legacy
    if callable(condition):
        return bool(condition(context))

    if not isinstance(condition, dict):
        return False

    cond_type = condition.get("type")
    params = condition.get("params") or {}

    if cond_type == "always_true":
        return True

    if cond_type == "inference_exists":
        inference_type = params.get("inference_type")
        if not inference_type:
            return False

        inferences = context.get("inferences") or []
        return inference_type in inferences

    return False


def has_inference(inference_type: str):
    return {
        "type": "inference_exists",
        "params": {
            "inference_type": inference_type,
        },
    }


def always_true():
    return {
        "type": "always_true",
    }
