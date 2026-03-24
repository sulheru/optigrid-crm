from pathlib import Path

path = Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/inferences/services.py")
text = path.read_text()

merge_import = "from apps.recommendations.merge_runtime import merge_persisted_recommendations_for_scope\n"
if merge_import not in text:
    lines = text.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, merge_import)
    text = "".join(lines)

if "merge_persisted_recommendations_for_scope(" in text:
    print("merge hook already present")
    path.write_text(text)
    raise SystemExit(0)

anchors = [
    "create_recommendations_from_llm_output(",
    "create_recommendation_from_inference(record)",
]

inserted = False

# Caso preferido: tras la llamada LLM
llm_idx = text.find("create_recommendations_from_llm_output(")
if llm_idx != -1:
    line_end = text.find("\n", llm_idx)
    while line_end != -1 and text[max(0, line_end - 1)] != ")":
        next_end = text.find("\n", line_end + 1)
        if next_end == -1:
            break
        line_end = next_end

    if line_end != -1:
        indent_start = text.rfind("\n", 0, llm_idx) + 1
        indent = text[indent_start:llm_idx]
        block = (
            f"\n{indent}merge_persisted_recommendations_for_scope(\n"
            f"{indent}    scope_type=record.source_type,\n"
            f"{indent}    scope_id=record.source_id,\n"
            f"{indent})\n"
        )
        text = text[:line_end + 1] + block + text[line_end + 1:]
        inserted = True

# Fallback: tras el bucle rules
if not inserted:
    marker = "create_recommendation_from_inference(record)"
    idx = text.find(marker)
    if idx != -1:
        line_end = text.find("\n", idx)
        indent_start = text.rfind("\n", 0, idx) + 1
        indent = text[indent_start:idx]
        block = (
            f"\n{indent}merge_persisted_recommendations_for_scope(\n"
            f"{indent}    scope_type=record.source_type,\n"
            f"{indent}    scope_id=record.source_id,\n"
            f"{indent})\n"
        )
        text = text[:line_end + 1] + block + text[line_end + 1:]
        inserted = True

if not inserted:
    raise SystemExit("Could not find insertion point in apps/inferences/services.py")

path.write_text(text)
print("patched apps/inferences/services.py")
