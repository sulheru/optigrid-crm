from apps.inferences.services import create_basic_email_inference
from apps.updates.services import create_basic_proposal


def process_email(email):
    print("[CRM_UPDATE_ENGINE][DEBUG] crm_update_engine.process_email.called", {"email_id": email.id})

    print("[CRM_UPDATE_ENGINE][EVENT] email_processing_started", {"email_id": email.id})

    # --- FACTS
    print("[CRM_UPDATE_ENGINE][EVENT] fact_extraction_started", {})

    # --- INFERENCES
    print("[CRM_UPDATE_ENGINE][EVENT] inference_generation_started", {})
    create_basic_email_inference(email)

    # --- PROPOSALS / RULE ENGINE
    print("[CRM_UPDATE_ENGINE][EVENT] crm_update_proposal_started", {})
    create_basic_proposal(email)

    # --- RECOMMENDATIONS
    print("[CRM_UPDATE_ENGINE][EVENT] recommendation_generation_started", {})

    print("[CRM_UPDATE_ENGINE][EVENT] email_processing_finished", {"email_id": email.id})


def handle_email(email):
    return process_email(email)
