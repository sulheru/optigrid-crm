from .conditions import always_true, has_inference


RULES = [
    {
        "name": "pricing_interest_detected",
        "priority": 100,
        "conditions": [
            has_inference("pricing_interest_signal"),
        ],
        "proposal": {
            "proposal_type": "prepare_pricing_response",
        },
        "final": True,
    },
    {
        "name": "default_fallback",
        "priority": 0,
        "conditions": [
            always_true(),
        ],
        "proposal": {
            "proposal_type": "followup",
        },
    },
]
