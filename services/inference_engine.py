# PATCH SAFE

def infer_from_fact(fact):
    # 🔥 COMPAT dict + object
    if isinstance(fact, dict):
        fact_type = fact.get("fact_type")
    else:
        fact_type = getattr(fact, "fact_type", None)

    if fact_type == "redirect_statement":
        yield {"type": "redirect_detected"}
