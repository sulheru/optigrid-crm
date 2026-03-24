from pathlib import Path

path = Path("apps/inferences/services.py")
code = path.read_text()

# import
if "services_llm" not in code:
    code = code.replace(
        "from apps.recommendations.services import create_recommendation_from_inference",
        "from apps.recommendations.services import create_recommendation_from_inference\nfrom apps.recommendations.services_llm import create_recommendations_from_llm_output",
    )

# insertar tras loop de inferencias
marker = "return created"

injection = """
    # --- NEW: LLM DIRECT RECOMMENDATIONS ---
    try:
        create_recommendations_from_llm_output(
            scope_type=source_type,
            scope_id=source_id,
            llm_result=result,
        )
    except Exception:
        pass
"""

code = code.replace(marker, injection + "\n" + marker)

path.write_text(code)
print("OK")
