def has_inference(inference_type: str):
    def _cond(context):
        return inference_type in context.get("inferences", [])
    return _cond


def not_(cond):
    def _cond(context):
        return not cond(context)
    return _cond
