from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from django.apps import apps


def _model(app_label: str, model_name: str):
    return apps.get_model(app_label, model_name)


def _optional_model(*candidates: tuple[str, str]):
    for app_label, model_name in candidates:
        try:
            return apps.get_model(app_label, model_name)
        except LookupError:
            continue
    return None


def _safe_attr(obj: Any, attr: str, default=None):
    return getattr(obj, attr, default)


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _serialize_datetime(value: Any):
    if value is None:
        return None
    try:
        return value.isoformat()
    except Exception:
        return str(value)


def _serialize_model(obj: Any, field_names: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for field_name in field_names:
        value = _safe_attr(obj, field_name)
        if hasattr(value, "isoformat"):
            value = _serialize_datetime(value)
        data[field_name] = value
    return data


def _append_unique_model(bucket: list[Any], obj: Any):
    if obj is None:
        return
    obj_id = _safe_attr(obj, "id")
    for existing in bucket:
        if _safe_attr(existing, "id") == obj_id:
            return
    bucket.append(obj)


def _normalize_scope_type(value: Any) -> str:
    raw = _coerce_text(value).lower()
    aliases = {
        "proposal": "proposal",
        "crm_update_proposal": "proposal",
        "update_proposal": "proposal",
        "inference": "inference",
        "inferencerecord": "inference",
        "inference_record": "inference",
        "fact": "fact",
        "factrecord": "fact",
        "fact_record": "fact",
        "email": "email_message",
        "emailmessage": "email_message",
        "email_message": "email_message",
        "thread": "thread",
    }
    return aliases.get(raw, raw)


@dataclass
class OpportunityAnalysisContext:
    opportunity: dict[str, Any]
    source_task: dict[str, Any] | None
    source_recommendation: dict[str, Any] | None
    proposal: dict[str, Any] | None
    inferences: list[dict[str, Any]]
    facts: list[dict[str, Any]]
    emails: list[dict[str, Any]]
    active_recommendations: list[dict[str, Any]]
    open_tasks: list[dict[str, Any]]
    summary_text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_opportunity_analysis_context(opportunity) -> OpportunityAnalysisContext:
    AIRecommendation = _model("recommendations", "AIRecommendation")
    CRMUpdateProposal = _model("updates", "CRMUpdateProposal")
    InferenceRecord = _model("inferences", "InferenceRecord")
    FactRecord = _model("facts", "FactRecord")
    OutboundEmail = _model("emailing", "OutboundEmail")
    InboundEmail = _model("emailing", "InboundEmail")

    CRMTask = _optional_model(
        ("tasks", "CRMTask"),
        ("tasks_app", "CRMTask"),
        ("crm_tasks", "CRMTask"),
    )

    opportunity_data = _serialize_model(
        opportunity,
        [
            "id",
            "title",
            "company_name",
            "stage",
            "estimated_value",
            "confidence",
            "summary",
            "created_at",
            "updated_at",
        ],
    )

    source_task = _safe_attr(opportunity, "source_task")
    source_task_data = None
    if source_task is not None:
        source_task_data = _serialize_model(
            source_task,
            [
                "id",
                "source_recommendation_id",
                "title",
                "description",
                "task_type",
                "status",
                "priority",
                "due_at",
                "created_at",
                "updated_at",
            ],
        )

    source_recommendation = _safe_attr(opportunity, "source_recommendation")
    if source_recommendation is None and source_task is not None:
        source_recommendation = _safe_attr(source_task, "source_recommendation")

    source_recommendation_data = None
    if source_recommendation is not None:
        source_recommendation_data = _serialize_model(
            source_recommendation,
            [
                "id",
                "scope_type",
                "scope_id",
                "recommendation_type",
                "recommendation_text",
                "confidence",
                "status",
                "created_at",
            ],
        )

    proposal = None
    seed_inferences: list[Any] = []
    seed_facts: list[Any] = []

    if source_recommendation is not None:
        scope_type = _normalize_scope_type(_safe_attr(source_recommendation, "scope_type"))
        scope_id = _coerce_text(_safe_attr(source_recommendation, "scope_id"))

        if scope_type == "proposal" and scope_id:
            try:
                proposal = CRMUpdateProposal.objects.filter(pk=scope_id).first()
            except Exception:
                proposal = None

        elif scope_type == "inference" and scope_id:
            try:
                inference = InferenceRecord.objects.filter(pk=scope_id).first()
                _append_unique_model(seed_inferences, inference)
            except Exception:
                pass

        elif scope_type == "fact" and scope_id:
            try:
                fact = FactRecord.objects.filter(pk=scope_id).first()
                _append_unique_model(seed_facts, fact)
            except Exception:
                pass

    if proposal is None:
        for attr_name in ("proposal", "source_proposal"):
            candidate = _safe_attr(opportunity, attr_name)
            if candidate is not None:
                proposal = candidate
                break

    proposal_data = None
    if proposal is not None:
        proposal_data = _serialize_model(
            proposal,
            [
                "id",
                "target_entity_type",
                "target_entity_id",
                "proposed_change_type",
                "proposed_payload",
                "confidence",
                "approval_required",
                "proposal_status",
                "created_at",
            ],
        )

    inferred_from_proposal: list[Any] = []
    if proposal is not None:
        try:
            for inference in InferenceRecord.objects.filter(
                source_type="proposal",
                source_id=str(proposal.id),
            ).order_by("id"):
                _append_unique_model(inferred_from_proposal, inference)
        except Exception:
            pass

    inference_models: list[Any] = []
    for item in seed_inferences:
        _append_unique_model(inference_models, item)
    for item in inferred_from_proposal:
        _append_unique_model(inference_models, item)

    for inference in inference_models:
        inf_source_type = _normalize_scope_type(_safe_attr(inference, "source_type"))
        inf_source_id = _coerce_text(_safe_attr(inference, "source_id"))

        if inf_source_type == "fact" and inf_source_id:
            try:
                fact = FactRecord.objects.filter(pk=inf_source_id).first()
                _append_unique_model(seed_facts, fact)
            except Exception:
                pass

    fact_models: list[Any] = []
    for item in seed_facts:
        _append_unique_model(fact_models, item)

    outbound_emails = list(
        OutboundEmail.objects.filter(opportunity=opportunity)
        .select_related("source_inbound")
        .order_by("-created_at")[:20]
    )
    inbound_emails = list(
        InboundEmail.objects.filter(opportunity=opportunity)
        .select_related("source_outbound")
        .order_by("-received_at", "-created_at")[:20]
    )

    emails_data: list[dict[str, Any]] = []

    for email in outbound_emails:
        emails_data.append(
            {
                "id": email.id,
                "direction": "outbound",
                "email_type": email.email_type,
                "counterparty": email.to_email,
                "subject": email.subject,
                "body_text": email.body,
                "status": email.status,
                "sent_at": _serialize_datetime(email.sent_at),
                "received_at": None,
                "created_at": _serialize_datetime(email.created_at),
            }
        )

    for email in inbound_emails:
        emails_data.append(
            {
                "id": email.id,
                "direction": "inbound",
                "email_type": "reply",
                "counterparty": email.from_email,
                "subject": email.subject,
                "body_text": email.body,
                "status": email.status,
                "reply_type": email.reply_type,
                "sent_at": None,
                "received_at": _serialize_datetime(email.received_at),
                "created_at": _serialize_datetime(email.created_at),
            }
        )

    emails_data.sort(
        key=lambda item: (
            item.get("received_at")
            or item.get("sent_at")
            or item.get("created_at")
            or ""
        ),
        reverse=True,
    )

    inferences_data = [
        _serialize_model(
            inference,
            [
                "id",
                "source_type",
                "source_id",
                "inference_type",
                "inference_value",
                "confidence",
                "rationale",
                "created_at",
            ],
        )
        for inference in inference_models
    ]

    facts_data = [
        _serialize_model(
            fact,
            [
                "id",
                "source_type",
                "source_id",
                "fact_type",
                "fact_value",
                "confidence",
                "observed_at",
                "created_at",
            ],
        )
        for fact in fact_models
    ]

    active_recommendations_qs = AIRecommendation.objects.filter(
        scope_type="opportunity",
        scope_id=str(opportunity.id),
    ).exclude(status="dismissed").order_by("-id")

    active_recommendations_data = [
        _serialize_model(
            item,
            [
                "id",
                "recommendation_type",
                "recommendation_text",
                "confidence",
                "status",
                "created_at",
            ],
        )
        for item in active_recommendations_qs
    ]

    open_tasks_data: list[dict[str, Any]] = []
    if CRMTask is not None:
        try:
            open_tasks_qs = CRMTask.objects.filter(
                opportunity_id=opportunity.id
            ).exclude(status__in=["done", "cancelled"]).order_by("id")

            open_tasks_data = [
                _serialize_model(
                    task,
                    [
                        "id",
                        "source_recommendation_id",
                        "title",
                        "description",
                        "task_type",
                        "status",
                        "priority",
                        "due_at",
                        "created_at",
                        "updated_at",
                    ],
                )
                for task in open_tasks_qs
            ]
        except Exception:
            open_tasks_data = []

    summary_parts: list[str] = []
    summary_parts.append(f"Opportunity #{opportunity.id}")
    summary_parts.append(f"Title: {_coerce_text(_safe_attr(opportunity, 'title'))}")
    summary_parts.append(f"Company: {_coerce_text(_safe_attr(opportunity, 'company_name'))}")
    summary_parts.append(f"Stage: {_coerce_text(_safe_attr(opportunity, 'stage'))}")
    summary_parts.append(f"Summary: {_coerce_text(_safe_attr(opportunity, 'summary'))}")

    if source_task is not None:
        summary_parts.append(
            "Source task: "
            f"{_coerce_text(_safe_attr(source_task, 'task_type'))} | "
            f"{_coerce_text(_safe_attr(source_task, 'title'))}"
        )

    if source_recommendation is not None:
        summary_parts.append(
            "Source recommendation: "
            f"{_coerce_text(_safe_attr(source_recommendation, 'recommendation_type'))} | "
            f"{_coerce_text(_safe_attr(source_recommendation, 'recommendation_text'))}"
        )
        summary_parts.append(
            "Recommendation scope: "
            f"{_coerce_text(_safe_attr(source_recommendation, 'scope_type'))} | "
            f"{_coerce_text(_safe_attr(source_recommendation, 'scope_id'))}"
        )

    if proposal is not None:
        summary_parts.append(
            "Proposal: "
            f"{_coerce_text(_safe_attr(proposal, 'proposed_change_type'))} | "
            f"status={_coerce_text(_safe_attr(proposal, 'proposal_status'))}"
        )

    if inferences_data:
        summary_parts.append("Inferences:")
        for item in inferences_data[:10]:
            summary_parts.append(f"- {item.get('inference_type')}: {item.get('inference_value')}")

    if facts_data:
        summary_parts.append("Facts:")
        for item in facts_data[:10]:
            summary_parts.append(f"- {item.get('fact_type')}: {item.get('fact_value')}")

    if emails_data:
        summary_parts.append("Emails:")
        for item in emails_data[:8]:
            body = _coerce_text(item.get("body_text"))
            when = item.get("received_at") or item.get("sent_at") or item.get("created_at")
            summary_parts.append(
                f"- [{item.get('direction')}] {item.get('subject')} | "
                f"{item.get('counterparty')} | {when} :: {body[:280]}"
            )

    return OpportunityAnalysisContext(
        opportunity=opportunity_data,
        source_task=source_task_data,
        source_recommendation=source_recommendation_data,
        proposal=proposal_data,
        inferences=inferences_data,
        facts=facts_data,
        emails=emails_data,
        active_recommendations=active_recommendations_data,
        open_tasks=open_tasks_data,
        summary_text="\n".join(part for part in summary_parts if part),
    )
