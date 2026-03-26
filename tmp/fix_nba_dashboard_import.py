from pathlib import Path

path = Path("apps/dashboard_views.py")
text = path.read_text(encoding="utf-8")

bad_prefix = "from apps.recommendations.nba import get_next_best_action_result\\n\\1"
good_prefix = "from apps.recommendations.nba import get_next_best_action_result"

if text.startswith(bad_prefix):
    text = good_prefix + text[len(bad_prefix):]
else:
    text = text.replace(
        "from apps.recommendations.nba import get_next_best_action_result\\n\\1",
        "from apps.recommendations.nba import get_next_best_action_result",
    )

path.write_text(text, encoding="utf-8")
print("[ok] dashboard_views.py import fixed")
