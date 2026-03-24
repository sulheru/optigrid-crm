from pathlib import Path

path = Path("apps/inferences/services.py")
code = path.read_text()

start = code.index("def create_inference(")
end = code.index("return created") + len("return created")

new_function = '''
def create_inference(
    *,
    source_type: str,
    source_id: int,
    input_text: str,
) -> list[InferenceRecord]:
    """
    Nuevo entrypoint IA-first.

    - usa LLMProvider (vía LLMClient)
    - genera inferencias
    - persiste resultados
    - dispara recommendations
    """

    llm = LLMClient()
    result = llm.analyze_email(input_text)

    created = []

    for inf in result.get("inferences", []):
        record = create_inference_record(
            source_type=source_type,
            source_id=source_id,
            inference_type=inf.get("type", "unknown"),
            inference_value=inf,
            confidence=inf.get("confidence", 0.7),
        )

        try:
            create_recommendation_from_inference(record)
        except Exception:
            pass

        created.append(record)

    # --- NEW: LLM DIRECT RECOMMENDATIONS ---
    try:
        from apps.recommendations.services_llm import create_recommendations_from_llm_output

        create_recommendations_from_llm_output(
            scope_type=source_type,
            scope_id=source_id,
            llm_result=result,
        )
    except Exception:
        pass

    return created
'''

new_code = code[:start] + new_function + code[end:]

path.write_text(new_code)
print("FIXED")
