from pathlib import Path
import re

ROOT = Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm")

py_files = [
    p for p in ROOT.rglob("*.py")
    if ".venv/" not in str(p)
    and "/migrations/" not in str(p)
    and "/__pycache__/" not in str(p)
]

governance_anchors = [
    "apply_governance(",
    "run_governance(",
    "govern_recommendations(",
    "apply_recommendation_governance(",
]

merge_import = "from apps.recommendations.merge import merge_recommendation_candidates\n"
merge_block = (
    "    merge_result = merge_recommendation_candidates(recommendations)\n"
    "    recommendations = merge_result.kept\n\n"
)

patched_governance = []
patched_llm_source = []

for path in py_files:
    text = path.read_text()

    if "merge_recommendation_candidates(" not in text:
        for anchor in governance_anchors:
            idx = text.find(anchor)
            if idx == -1:
                continue

            line_start = text.rfind("\n", 0, idx) + 1
            indent = text[line_start:idx]
            if "recommendations" not in text[max(0, idx - 600):idx + 300]:
                continue

            if merge_import not in text:
                lines = text.splitlines(True)
                inserted = False
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        continue
                    lines.insert(i, merge_import)
                    inserted = True
                    break
                if not inserted:
                    lines.insert(0, merge_import)
                text = "".join(lines)
                idx = text.find(anchor)
                line_start = text.rfind("\n", 0, idx) + 1
                indent = text[line_start:idx]

            block = merge_block.replace("    ", indent)
            text = text[:line_start] + block + text[line_start:]
            path.write_text(text)
            patched_governance.append(str(path))
            break

for path in py_files:
    if "llm" not in path.name.lower() and "llm" not in str(path).lower():
        continue

    text = path.read_text()

    def repl(match):
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
        prefix += "\n                source=AIRecommendation.SOURCE_LLM"
        return prefix + suffix

    new_text = re.sub(
        r"AIRecommendation\.objects\.create\((.*?)\)",
        repl,
        text,
        flags=re.DOTALL,
    )

    if new_text != text:
        path.write_text(new_text)
        patched_llm_source.append(str(path))

print("PATCHED_GOVERNANCE")
for item in patched_governance:
    print(item)

print("PATCHED_LLM_SOURCE")
for item in patched_llm_source:
    print(item)

if not patched_governance:
    print("NO_GOVERNANCE_HOOK_FOUND")
