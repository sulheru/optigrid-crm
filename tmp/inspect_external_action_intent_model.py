from apps.external_actions.models import ExternalActionIntent

print("\n=== MODEL: ExternalActionIntent ===\n")

for field in ExternalActionIntent._meta.get_fields():
    if hasattr(field, "attname"):
        print({
            "name": field.name,
            "type": field.__class__.__name__,
            "null": getattr(field, "null", None),
            "blank": getattr(field, "blank", None),
            "default": getattr(field, "default", None),
        })

print("\n=== INTENT TYPES ===\n")

if hasattr(ExternalActionIntent, "IntentType"):
    for attr in dir(ExternalActionIntent.IntentType):
        if attr.isupper():
            print(attr, getattr(ExternalActionIntent.IntentType, attr))
else:
    print("No IntentType enum found")
