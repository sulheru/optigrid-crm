from apps.inferences.services import create_basic_email_inference


def process_email(email):
    print("[CRM_UPDATE_ENGINE][DEBUG] crm_update_engine.process_email.called", {"email_id": email.id})

    print("[CRM_UPDATE_ENGINE][EVENT] email_processing_started", {"email_id": email.id})

    # --- FACTS (placeholder)
    print("[CRM_UPDATE_ENGINE][EVENT] fact_extraction_started", {})

    # --- INFERENCES (CRÍTICO)
    print("[CRM_UPDATE_ENGINE][EVENT] inference_generation_started", {})
    create_basic_email_inference(email)  # 🔴 ESTO ES LO QUE FALTA

    # --- PROPOSALS
    print("[CRM_UPDATE_ENGINE][EVENT] crm_update_proposal_started", {})

    # --- RECOMMENDATIONS
    print("[CRM_UPDATE_ENGINE][EVENT] recommendation_generation_started", {})

    print("[CRM_UPDATE_ENGINE][EVENT] email_processing_finished", {"email_id": email.id})


# Compatibilidad con tests existentes
def handle_email(email):
    return process_email(email)
