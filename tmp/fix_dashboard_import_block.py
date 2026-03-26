from pathlib import Path

path = Path("apps/dashboard_views.py")
text = path.read_text()

bad_block = """from apps.core.ui_semantics import (
from django.shortcuts import render
    get_priority_level,
    get_recommendation_ui,
)"""

good_block = """from django.shortcuts import render

from apps.core.ui_semantics import (
    get_priority_level,
    get_recommendation_ui,
)"""

if bad_block in text:
    text = text.replace(bad_block, good_block)
    path.write_text(text)
    print("[ok] import block fixed")
else:
    print("[warn] pattern not found, manual check needed")
