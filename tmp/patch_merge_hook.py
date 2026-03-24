from pathlib import Path

CANDIDATES = [
    Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/inferences/services.py"),
    Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/services.py"),
]

import_line = "from apps.recommendations.merge import merge_recommendation_candidates\n"

hook_snippets = [
    (
        "governed_recommendations =",
        """merge_result = merge_recommendation_candidates(recommendations)
recommendations = merge_result.kept

""",
    ),
    (
        "recommendations = apply_governance(",
        """merge_result = merge_recommendation_candidates(recommendations)
recommendations = merge_result.kept

""",
    ),
    (
        "recommendations = run_governance(",
        """merge_result = merge_recommendation_candidates(recommendations)
recommendations = merge_result.kept

""",
    ),
]

for path in CANDIDATES:
    if not path.exists():
        continue

    text = path.read_text()

    if "merge_recommendation_candidates(" in text:
        print(f"{path.name} already patched")
        raise SystemExit(0)

    if import_line not in text:
        lines = text.splitlines(True)
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith("from apps.recommendations") or line.startswith("from apps.inferences"):
                lines.insert(i, import_line)
                inserted = True
                break
        if not inserted:
            lines.insert(0, import_line)
        text = "".join(lines)

    for anchor, block in hook_snippets:
        idx = text.find(anchor)
        if idx != -1:
            text = text[:idx] + block + text[idx:]
            path.write_text(text)
            print(f"Patched merge hook in {path}")
            raise SystemExit(0)

raise SystemExit("Could not locate governance hook anchor automatically")
