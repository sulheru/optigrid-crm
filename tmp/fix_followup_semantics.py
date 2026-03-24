from pathlib import Path

path = Path("apps/recommendations/execution.py")
text = path.read_text()

# 1. followup -> task (no draft)
text = text.replace(
    'if recommendation_type in {"reply_strategy", "followup"}:',
    'if recommendation_type == "reply_strategy":'
)

# insertar bloque followup justo después
insert_block = '''
    elif recommendation_type == "followup":
        task = materialize_recommendation_as_task(recommendation)
        result.created_entities["task_id"] = task.id
        result.side_effects.append("task_materialized")
'''

text = text.replace(
    'elif recommendation_type == "contact_strategy":',
    insert_block + '\n    elif recommendation_type == "contact_strategy":'
)

path.write_text(text)
print("patched followup semantics")


# 2. recompilar
import subprocess

subprocess.run([
    "python3", "-m", "py_compile",
    "apps/recommendations/execution.py"
], check=True)

# 3. tests emailing (rápido)
subprocess.run([
    "python3", "manage.py", "test", "apps.emailing.tests"
])
