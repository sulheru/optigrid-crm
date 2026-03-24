from pathlib import Path

settings_path = Path("config/settings.py")
settings_code = settings_path.read_text()

block = """
# === LLM Governance Layer V1 ===
LLM_OUTPUT_MODE = "hybrid"  # inference_only | hybrid | llm_driven
LLM_MIN_CONFIDENCE = 0.70
LLM_ALLOWED_RECOMMENDATION_TYPES = [
    "followup",
    "contact_strategy",
    "reply_strategy",
    "opportunity_review",
    "pricing_strategy",
    "advance_opportunity",
    "mark_lost",
]
"""

if "LLM_OUTPUT_MODE" not in settings_code:
    settings_code = settings_code.rstrip() + "\n\n" + block.strip() + "\n"

settings_path.write_text(settings_code)
print("settings.py: OK")
