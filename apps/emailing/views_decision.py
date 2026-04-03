from django.http import Http404
from django.shortcuts import render

from apps.emailing.decision_detail import get_email_decision_view
from apps.emailing.models import InboundEmail


def _is_meaningful_decision_output(decision_output) -> bool:
    if not isinstance(decision_output, dict):
        return False

    selected_rules = decision_output.get("selected_rules") or []
    discarded_rules = decision_output.get("discarded_rules") or []
    final_effect = decision_output.get("final_effect")

    return bool(selected_rules or discarded_rules or final_effect)


def _normalize_explanation(decision_output, explanation):
    if isinstance(explanation, list):
        return [item for item in explanation if isinstance(item, str)]

    if isinstance(decision_output, dict):
        maybe_explanation = decision_output.get("explanation")
        if isinstance(maybe_explanation, list):
            return [item for item in maybe_explanation if isinstance(item, str)]

    return []


def _normalize_final_effect(decision_output):
    if not isinstance(decision_output, dict):
        return None

    final_effect = decision_output.get("final_effect")
    if isinstance(final_effect, dict) and final_effect:
        return final_effect

    return None


def _normalize_semantic_effect(semantic_effect, final_effect):
    if isinstance(semantic_effect, dict) and semantic_effect:
        return semantic_effect

    if isinstance(final_effect, dict):
        maybe_semantic_effect = final_effect.get("semantic_effect")
        if isinstance(maybe_semantic_effect, dict) and maybe_semantic_effect:
            return maybe_semantic_effect

    return None


def _normalize_decision_detail_context(context: dict) -> dict:
    context = dict(context or {})

    decision_output = context.get("decision_output")
    inbound_decision = context.get("inbound_decision")

    final_effect = _normalize_final_effect(decision_output)
    explanation = _normalize_explanation(
        decision_output=decision_output,
        explanation=context.get("explanation"),
    )
    semantic_effect = _normalize_semantic_effect(
        semantic_effect=context.get("semantic_effect"),
        final_effect=final_effect,
    )

    has_decision_output = _is_meaningful_decision_output(decision_output)
    has_operational_decision = inbound_decision is not None
    has_trace = context.get("trace") is not None

    if has_decision_output:
        detail_state = "full"
        state = "decision"
    elif has_operational_decision:
        detail_state = "operational_only"
        state = "operational"
    else:
        detail_state = "empty"
        state = "empty"

    context["decision_output"] = decision_output if isinstance(decision_output, dict) else None
    context["final_effect"] = final_effect
    context["explanation"] = explanation
    context["semantic_effect"] = semantic_effect
    context["inbound_decision"] = inbound_decision
    context["has_decision_output"] = has_decision_output
    context["has_operational_decision"] = has_operational_decision
    context["has_trace"] = has_trace
    context["has_trace_details"] = has_decision_output or has_trace or bool(semantic_effect) or bool(explanation)
    context["detail_state"] = detail_state
    context["state"] = state

    return context


def email_decision_detail(request, email_id: int):
    try:
        context = get_email_decision_view(email_id)
    except InboundEmail.DoesNotExist as exc:
        raise Http404("Email not found") from exc

    context = _normalize_decision_detail_context(context)
    return render(request, "emailing/decision_detail.html", context)
