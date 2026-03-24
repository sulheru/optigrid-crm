from pathlib import Path
import re

path = Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/services_llm.py")
text = path.read_text()

if "SOURCE_LLM" in text and "source=" in text:
    print("Already patched")
    raise SystemExit(0)

def inject_source(match):
    block = match.group(0)
    if "source=" in block:
        return block

    insert_at = block.rfind(")")
    if insert_at == -1:
        return block

    prefix = block[:insert_at].rstrip()
    suffix = block[insert_at:]

    if not prefix.endswith(","):
        prefix += ","

    prefix += "\n        source=AIRecommendation.SOURCE_LLM"

    return prefix + suffix


new_text = re.sub(
    r"AIRecommendation\.objects\.create\((.*?)\)",
    inject_source,
    text,
    flags=re.DOTALL,
)

if new_text == text:
    raise SystemExit("No changes applied")

path.write_text(new_text)
print("Patched successfully")
