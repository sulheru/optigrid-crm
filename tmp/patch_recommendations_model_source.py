from pathlib import Path

path = Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/models.py")
text = path.read_text()

if 'name="source"' in text or "source = models.CharField(" in text:
    print("models.py already contains source field")
    raise SystemExit(0)

anchor = "status = models.CharField("
idx = text.find(anchor)
if idx == -1:
    raise SystemExit("Could not find status field anchor in models.py")

insert_at = text.find("\n", idx)
insert_block = """

    SOURCE_RULES = "rules"
    SOURCE_LLM = "llm"
    SOURCE_MERGED = "merged"
    SOURCE_CHOICES = [
        (SOURCE_RULES, "Rules"),
        (SOURCE_LLM, "LLM"),
        (SOURCE_MERGED, "Merged"),
    ]

    source = models.CharField(
        max_length=16,
        choices=SOURCE_CHOICES,
        default=SOURCE_RULES,
        db_index=True,
    )
"""
text = text[:insert_at] + insert_block + text[insert_at:]
path.write_text(text)
print("Patched models.py")
