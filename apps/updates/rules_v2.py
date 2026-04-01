RULES = [
    {
        "name": "pricing_interest_detected",
        "priority": 100,
        "conditions": [
            lambda ctx: "pricing_interest_signal" in ctx["inferences"]
        ],
        "proposal": {
            "proposal_type": "prepare_pricing_response",
        },
        "final": True,
    },
    {
        "name": "default_fallback",
        "priority": 0,
        "conditions": [],
        "proposal": {
            "proposal_type": "followup",  # ← CAMBIO CLAVE
        },
    },
]
