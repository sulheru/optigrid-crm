from .conditions import has_inference


PRICING_RULES = [
    {
        "name": "pricing_interest_detected",
        "priority": 100,
        "outcome": "final",
        "conditions": [
            has_inference("pricing_interest_signal")
        ],
        "proposal": {
            "proposal_type": "prepare_pricing_response",
            "payload": {},
        },
    },
]


FALLBACK_RULES = [
    {
        "name": "default_fallback",
        "priority": 0,
        "outcome": "fallback",
        "conditions": [],
        "proposal": {
            "proposal_type": "review_manually",
            "payload": {},
        },
    },
]


RULES = [
    *PRICING_RULES,
    *FALLBACK_RULES,
]
