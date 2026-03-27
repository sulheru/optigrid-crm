from pathlib import Path

settings_path = Path("config/settings.py")
text = settings_path.read_text()

if "apps.external_actions" in text:
    print("[ok] apps.external_actions already present")
    raise SystemExit(0)

needle = "INSTALLED_APPS = ["
idx = text.find(needle)
if idx == -1:
    raise SystemExit("Could not find INSTALLED_APPS in config/settings.py")

insert_at = idx + len(needle)
replacement = needle + "\n    'apps.external_actions',"
text = text[:idx] + replacement + text[insert_at:]

settings_path.write_text(text)
print("[ok] added apps.external_actions to config/settings.py")
