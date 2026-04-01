from importlib import import_module, reload
from .rules_registry import RULE_SETS, DEFAULT_RULE_SET


def get_rules(context, version=None):
    version = version or DEFAULT_RULE_SET

    module_path = RULE_SETS[version]

    module = import_module(module_path)
    module = reload(module)  # ← CLAVE

    return module.RULES
