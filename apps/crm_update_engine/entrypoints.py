print("🔥 ENTRYPOINT LOADED")

from apps.facts.services import create_email_fact
from apps.inferences.services import create_basic_email_inference
from apps.updates.services import create_basic_proposal
from apps.recommendations.services_engine import create_basic_email_recommendation


def process_email(email):
    print("🔥 ENTRYPOINT EXECUTED")

    print("[CRM_UPDATE_ENGINE][DEBUG] crm_update_engine.process_email.called", {"email_id": email.id})

    print("[CRM_UPDATE_ENGINE][EVENT] email_processing_started", {"email_id": email.id})

    # --- FACTS
    print("[CRM_UPDATE_ENGINE][EVENT] fact_extraction_started", {})
    create_email_fact(email)

    # --- INFERENCES
    print("[CRM_UPDATE_ENGINE][EVENT] inference_generation_started", {})
    create_basic_email_inference(email)

    # --- PROPOSALS
    print("[CRM_UPDATE_ENGINE][EVENT] crm_update_proposal_started", {})
    create_basic_proposal(email)

    # --- RECOMMENDATIONS
    print("[CRM_UPDATE_ENGINE][EVENT] recommendation_generation_started", {})
    create_basic_email_recommendation(email)

    print("[CRM_UPDATE_ENGINE][EVENT] email_processing_finished", {"email_id": email.id})
