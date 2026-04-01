from .rules import PRICING_RULES, FALLBACK_RULES


DEFAULT_RULE_SET = [
    *PRICING_RULES,
    *FALLBACK_RULES,
]


CORP_A_RULE_SET = [
    *PRICING_RULES,
    *FALLBACK_RULES,
    # futuro: reglas específicas
]


RULE_SETS = {
    None: DEFAULT_RULE_SET,
    "corp_a": CORP_A_RULE_SET,
}
