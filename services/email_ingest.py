from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from apps.emailing.models import EmailMessage
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from services.events import record_event
from services.fact_extraction import create_facts_from_email
from services.inference_engine import create_inferences_from_fact
from services.update_proposals import create_update_proposal_from_inference


@dataclass
class EmailProcessingResult:
    email_id: int
    facts_created: int
    inferences_created: int
    proposals_created: int


def _has_model_field(instance, field_name: str) -> bool:
    return any(
        getattr(f, "concrete", False) and f.name == field_name
        for f in instance._meta.get_fields()
    )


@transaction.atomic
def process_email_message(email: EmailMessage) -> EmailProcessingResult:
    """
    Orquesta el vertical slice:
    EmailMessage -> FactRecord -> InferenceRecord -> CRMUpdateProposal -> Event
    """
    facts: list[FactRecord] = create_facts_from_email(email)

    if facts:
        record_event(
            event_type="email_message_parsed",
            aggregate_type="email_message",
            aggregate_id=email.id,
            payload={"facts_detected": len(facts)},
            triggered_by_type="system",
        )

    created_inferences: list[InferenceRecord] = []
    created_proposals: list[CRMUpdateProposal] = []

    for fact in facts:
        record_event(
            event_type="fact_recorded",
            aggregate_type="fact_record",
            aggregate_id=fact.id,
            payload={
                "source_type": fact.source_type,
                "source_id": fact.source_id,
                "fact_type": fact.fact_type,
            },
            triggered_by_type="system",
        )

        inference_records = create_inferences_from_fact(fact)
        created_inferences.extend(inference_records)

        for inference in inference_records:
            record_event(
                event_type="inference_created",
                aggregate_type="inference_record",
                aggregate_id=inference.id,
                payload={
                    "source_type": inference.source_type,
                    "source_id": inference.source_id,
                    "inference_type": inference.inference_type,
                },
                triggered_by_type="system",
            )

            proposal = create_update_proposal_from_inference(inference)
            if proposal is not None:
                created_proposals.append(proposal)

                record_event(
                    event_type="crm_update_proposed",
                    aggregate_type="crm_update_proposal",
                    aggregate_id=proposal.id,
                    payload={
                        "target_entity_type": proposal.target_entity_type,
                        "proposed_change_type": proposal.proposed_change_type,
                        "approval_required": proposal.approval_required,
                    },
                    triggered_by_type="ai_agent",
                    triggered_by_id="email_ingest_pipeline",
                )

                if proposal.approval_required:
                    record_event(
                        event_type="crm_update_marked_for_approval",
                        aggregate_type="crm_update_proposal",
                        aggregate_id=proposal.id,
                        payload={"proposal_status": proposal.proposal_status},
                        triggered_by_type="system",
                    )

    if _has_model_field(email, "message_status"):
        email.message_status = "actioned" if created_proposals else "classified"
        email.save(update_fields=["message_status"])

    return EmailProcessingResult(
        email_id=email.id,
        facts_created=len(facts),
        inferences_created=len(created_inferences),
        proposals_created=len(created_proposals),
    )
