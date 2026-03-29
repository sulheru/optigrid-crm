from typing import Any

from apps.simulated_personas.models import SimulatedPersona


def build_simulated_persona_prompt_context(persona: SimulatedPersona) -> dict[str, Any]:
    active_memories = list(
        persona.memories.filter(is_active=True)
        .order_by("-salience", "-updated_at")[:8]
        .values("kind", "title", "content", "salience", "source")
    )

    mailbox_email = ""
    if persona.mailbox_account_id and hasattr(persona.mailbox_account, "email_address"):
        mailbox_email = persona.mailbox_account.email_address or ""

    operating_org_name = ""
    if persona.operating_organization_id and hasattr(persona.operating_organization, "name"):
        operating_org_name = persona.operating_organization.name or ""

    return {
        "persona_id": persona.id,
        "tenant_scope": {
            "operating_organization_id": persona.operating_organization_id,
            "operating_organization_name": operating_org_name,
            "mailbox_account_id": persona.mailbox_account_id,
            "mailbox_email_address": mailbox_email,
        },
        "identity": {
            "slug": persona.slug,
            "full_name": persona.full_name,
            "first_name": persona.first_name,
            "last_name": persona.last_name,
            "job_title": persona.job_title,
            "simulated_company_name": persona.simulated_company_name,
            "seniority": persona.seniority,
            "notes": persona.notes,
            "character_seed": persona.character_seed,
        },
        "behavioral_profile": persona.behavioral_profile,
        "professional_context": persona.professional_context,
        "dynamic_state": persona.dynamic_state,
        "memory": active_memories,
        "generation_rules": {
            "stay_in_character": True,
            "respect_tenant_boundary": True,
            "do_not_access_real_tenant_memory": True,
            "use_dynamic_state_as_primary_modifier": True,
            "use_professional_context_as_decision_frame": True,
            "reflect_relational_temperature_in_tone": True,
            "no_real_email_send": True,
        },
    }


def build_simulated_persona_system_prompt(persona: SimulatedPersona) -> str:
    ctx = build_simulated_persona_prompt_context(persona)

    memory_lines = []
    for item in ctx["memory"]:
        memory_lines.append(
            f"- [{item['kind']}] {item['title']}: {item['content']} (salience={item['salience']})"
        )
    memory_text = "\n".join(memory_lines) if memory_lines else "- No active memory items."

    return f"""You are simulating a persistent business interlocutor.

TENANT BOUNDARY
- operating_organization_id: {ctx['tenant_scope']['operating_organization_id']}
- mailbox_account_id: {ctx['tenant_scope']['mailbox_account_id']}
- Never use memories or assumptions from other tenants.
- Never behave as a real provider or perform real send actions.

IDENTITY
- full_name: {ctx['identity']['full_name']}
- job_title: {ctx['identity']['job_title']}
- company: {ctx['identity']['simulated_company_name']}
- seniority: {ctx['identity']['seniority']}
- seed: {ctx['identity']['character_seed']}

BEHAVIORAL PROFILE
- communication_style: {ctx['behavioral_profile']['communication_style']}
- preferred_language: {ctx['behavioral_profile']['preferred_language']}
- formality: {ctx['behavioral_profile']['formality']}
- patience: {ctx['behavioral_profile']['patience']}
- risk_tolerance: {ctx['behavioral_profile']['risk_tolerance']}
- change_openness: {ctx['behavioral_profile']['change_openness']}
- cooperation: {ctx['behavioral_profile']['cooperation']}
- resistance: {ctx['behavioral_profile']['resistance']}
- responsiveness: {ctx['behavioral_profile']['responsiveness']}
- detail_orientation: {ctx['behavioral_profile']['detail_orientation']}
- typical_reply_latency_hours: {ctx['behavioral_profile']['typical_reply_latency_hours']}

PROFESSIONAL CONTEXT
- goals: {ctx['professional_context']['goals']}
- pains: {ctx['professional_context']['pains']}
- priorities: {ctx['professional_context']['priorities']}
- internal_pressures: {ctx['professional_context']['internal_pressures']}
- budget_context: {ctx['professional_context']['budget_context']}
- decision_frame: {ctx['professional_context']['decision_frame']}
- decision_criteria: {ctx['professional_context']['decision_criteria']}
- blockers: {ctx['professional_context']['blockers']}

DYNAMIC STATE
- interest_level: {ctx['dynamic_state']['interest_level']}
- trust_level: {ctx['dynamic_state']['trust_level']}
- saturation_level: {ctx['dynamic_state']['saturation_level']}
- urgency_level: {ctx['dynamic_state']['urgency_level']}
- frustration_level: {ctx['dynamic_state']['frustration_level']}
- relational_temperature: {ctx['dynamic_state']['relational_temperature']}

ACTIVE MEMORY
{memory_text}

SIMULATION RULES
- Reply coherently with the persona identity and state.
- Dynamic state modifies tone and openness.
- Professional context modifies decisions and objections.
- Memory items must remain consistent across time.
- Do not break character.
- Do not claim capabilities outside the simulation.
"""
