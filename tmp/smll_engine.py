from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from apps.simulated_personas.models import SimulatedPersona, SimulatedPersonaMemory
from apps.simulated_personas.services.prompt_builder import (
    build_simulated_persona_prompt_context,
    build_simulated_persona_system_prompt,
)


DECIMAL_ZERO = Decimal("0.00")
DECIMAL_ONE = Decimal("1.00")


@dataclass(slots=True)
class SimulatedIncomingMessage:
    subject: str
    body: str
    sender_name: str = ""
    sender_email: str = ""
    thread_key: str = ""
    mailbox_account_id: int | None = None


@dataclass(slots=True)
class SimulatedReplyResult:
    persona_id: int
    persona_slug: str
    mailbox_account_id: int
    subject: str
    reply_body: str
    prompt_context: dict
    system_prompt: str
    state_before: dict
    state_after: dict
    detected_signals: list[str]
    memory_created: bool


def resolve_simulated_persona(
    *,
    operating_organization,
    persona_id: int | None = None,
    persona_slug: str | None = None,
    mailbox_account=None,
) -> SimulatedPersona:
    qs = SimulatedPersona.objects.active().filter(
        operating_organization=operating_organization,
    )

    if persona_id is not None:
        persona = qs.filter(id=persona_id).first()
        if persona is None:
            raise ValueError("No existe SimulatedPersona con ese persona_id en este tenant.")
        return persona

    if persona_slug:
        persona = qs.filter(slug=persona_slug).first()
        if persona is None:
            raise ValueError("No existe SimulatedPersona con ese slug en este tenant.")
        return persona

    if mailbox_account is not None:
        persona = qs.filter(mailbox_account=mailbox_account).order_by("id").first()
        if persona is not None:
            return persona

    persona = qs.order_by("id").first()
    if persona is None:
        raise ValueError("No existe ninguna SimulatedPersona activa en este tenant.")
    return persona


def build_simulated_reply(
    *,
    operating_organization,
    incoming_message: SimulatedIncomingMessage,
    persona_id: int | None = None,
    persona_slug: str | None = None,
    mailbox_account=None,
    persist_memory: bool = True,
    update_state: bool = True,
) -> SimulatedReplyResult:
    persona = resolve_simulated_persona(
        operating_organization=operating_organization,
        persona_id=persona_id,
        persona_slug=persona_slug,
        mailbox_account=mailbox_account,
    )

    resolved_mailbox = mailbox_account or persona.mailbox_account
    if resolved_mailbox is None:
        raise ValueError(
            "SMLL runtime requiere mailbox resuelto. "
            "La persona no tiene mailbox_account y no se proporcionó uno explícitamente."
        )

    state_before = persona.dynamic_state
    detected_signals = _detect_signals(incoming_message)
    state_deltas = _derive_state_deltas(detected_signals, incoming_message.body)
    reply_body = _compose_reply_body(persona, incoming_message, detected_signals)
    subject = _build_reply_subject(incoming_message.subject)
    memory_created = False

    with transaction.atomic():
        if update_state:
            persona.apply_state_delta(
                interest_delta=state_deltas["interest_delta"],
                trust_delta=state_deltas["trust_delta"],
                saturation_delta=state_deltas["saturation_delta"],
                urgency_delta=state_deltas["urgency_delta"],
                frustration_delta=state_deltas["frustration_delta"],
                relational_temperature=state_deltas["relational_temperature"],
                save=False,
            )
            persona.last_interaction_at = timezone.now()
            persona.mailbox_account = resolved_mailbox
            persona.save(
                update_fields=[
                    "interest_level",
                    "trust_level",
                    "saturation_level",
                    "urgency_level",
                    "frustration_level",
                    "relational_temperature",
                    "last_interaction_at",
                    "mailbox_account",
                    "state_last_updated_at",
                    "updated_at",
                ]
            )

        if persist_memory:
            memory_created = _persist_interaction_memory(
                persona=persona,
                incoming_message=incoming_message,
                detected_signals=detected_signals,
            )

    prompt_context = build_simulated_persona_prompt_context(persona)
    system_prompt = build_simulated_persona_system_prompt(persona)

    return SimulatedReplyResult(
        persona_id=persona.id,
        persona_slug=persona.slug,
        mailbox_account_id=resolved_mailbox.id,
        subject=subject,
        reply_body=reply_body,
        prompt_context=prompt_context,
        system_prompt=system_prompt,
        state_before=state_before,
        state_after=persona.dynamic_state,
        detected_signals=detected_signals,
        memory_created=memory_created,
    )


def _build_reply_subject(subject: str) -> str:
    clean_subject = (subject or "").strip()
    if not clean_subject:
        return "Re: your message"
    if clean_subject.lower().startswith("re:"):
        return clean_subject
    return f"Re: {clean_subject}"


def _detect_signals(incoming_message: SimulatedIncomingMessage) -> list[str]:
    haystack = f"{incoming_message.subject}\n{incoming_message.body}".lower()
    signals: list[str] = []

    signal_patterns = [
        ("positive_interest", ["interested", "sounds good", "let's talk", "review", "could be relevant", "would like"]),
        ("meeting_request", ["meeting", "call", "teams", "zoom", "availability", "schedule"]),
        ("budget_pressure", ["budget", "cost", "price", "too expensive", "limited budget"]),
        ("urgency", ["urgent", "asap", "this week", "soon", "immediately"]),
        ("skepticism", ["not sure", "skeptical", "concern", "unclear", "why", "prove"]),
        ("rejection", ["not interested", "no interest", "stop", "unsubscribe", "not now"]),
        ("delay", ["later", "next quarter", "in may", "not now", "follow up later"]),
        ("change_opportunity", ["improve", "change", "replace", "migration", "modernize"]),
        ("risk_sensitivity", ["risk", "security", "compliance", "reliability"]),
        ("friction", ["too many emails", "generic", "spam", "tired of vendors"]),
    ]

    for signal_name, patterns in signal_patterns:
        if any(pattern in haystack for pattern in patterns):
            signals.append(signal_name)

    if not signals:
        signals.append("neutral")

    return signals


def _derive_state_deltas(signals: Iterable[str], body: str) -> dict:
    interest_delta = Decimal("0.00")
    trust_delta = Decimal("0.00")
    saturation_delta = Decimal("0.02")
    urgency_delta = Decimal("0.00")
    frustration_delta = Decimal("0.00")
    relational_temperature = None

    signals = list(signals)

    if "positive_interest" in signals:
        interest_delta += Decimal("0.12")
        trust_delta += Decimal("0.05")
        relational_temperature = SimulatedPersona.Temperature.WARM

    if "meeting_request" in signals:
        interest_delta += Decimal("0.08")
        trust_delta += Decimal("0.04")
        urgency_delta += Decimal("0.08")
        relational_temperature = SimulatedPersona.Temperature.ENGAGED

    if "budget_pressure" in signals:
        risk_adjustment = Decimal("0.04")
        interest_delta -= Decimal("0.02")
        frustration_delta += risk_adjustment

    if "urgency" in signals:
        urgency_delta += Decimal("0.20")
        saturation_delta += Decimal("0.06")

    if "skepticism" in signals:
        trust_delta -= Decimal("0.04")
        frustration_delta += Decimal("0.03")
        relational_temperature = SimulatedPersona.Temperature.GUARDED

    if "rejection" in signals:
        interest_delta -= Decimal("0.20")
        trust_delta -= Decimal("0.10")
        frustration_delta += Decimal("0.08")
        relational_temperature = SimulatedPersona.Temperature.COLD

    if "delay" in signals:
        urgency_delta -= Decimal("0.06")
        interest_delta -= Decimal("0.03")

    if "change_opportunity" in signals:
        interest_delta += Decimal("0.05")

    if "risk_sensitivity" in signals:
        trust_delta -= Decimal("0.01")

    if "friction" in signals:
        frustration_delta += Decimal("0.10")
        saturation_delta += Decimal("0.08")
        relational_temperature = SimulatedPersona.Temperature.FRICTION

    if len(body or "") > 1200:
        saturation_delta += Decimal("0.04")

    return {
        "interest_delta": interest_delta,
        "trust_delta": trust_delta,
        "saturation_delta": saturation_delta,
        "urgency_delta": urgency_delta,
        "frustration_delta": frustration_delta,
        "relational_temperature": relational_temperature,
    }


def _compose_reply_body(
    persona: SimulatedPersona,
    incoming_message: SimulatedIncomingMessage,
    detected_signals: list[str],
) -> str:
    greeting = _build_greeting(persona, incoming_message)
    acknowledgement = _build_acknowledgement(persona, detected_signals)
    stance = _build_stance(persona, detected_signals)
    next_step = _build_next_step(persona, detected_signals)
    signoff = _build_signoff(persona)

    sections = [greeting, "", acknowledgement, stance, next_step, "", signoff]
    return "\n".join(section for section in sections if section is not None).strip()


def _build_greeting(persona: SimulatedPersona, incoming_message: SimulatedIncomingMessage) -> str:
    sender_name = (incoming_message.sender_name or "").strip()

    if Decimal(persona.formality) >= Decimal("0.70"):
        if sender_name:
            return f"Hello {sender_name},"
        return "Hello,"
    if sender_name:
        return f"Hi {sender_name},"
    return "Hi,"


def _build_acknowledgement(persona: SimulatedPersona, detected_signals: list[str]) -> str:
    style = persona.communication_style

    if "rejection" in detected_signals:
        if style == SimulatedPersona.CommunicationStyle.DIRECT:
            return "Thanks for the clarity."
        return "Thank you for being clear about the current situation."

    if "meeting_request" in detected_signals:
        if style == SimulatedPersona.CommunicationStyle.CONCISE:
            return "Thanks. A short discussion makes sense."
        return "Thank you. A focused conversation would be useful here."

    if "positive_interest" in detected_signals:
        if style == SimulatedPersona.CommunicationStyle.EXPLANATORY:
            return "Thank you for the note. The topic is relevant from my perspective as well."
        return "Thanks for reaching out. This looks relevant."

    if "budget_pressure" in detected_signals:
        return "Thank you. Budget is naturally part of the decision."

    return "Thank you for your message."


def _build_stance(persona: SimulatedPersona, detected_signals: list[str]) -> str:
    goals = persona.goals or []
    pains = persona.pains or []
    priorities = persona.priorities or []
    blockers = persona.blockers or []

    sentences: list[str] = []

    if "friction" in detected_signals:
        sentences.append(
            "I tend to filter aggressively when outreach feels generic, so relevance and specificity matter."
        )

    if "budget_pressure" in detected_signals:
        sentences.append(
            "Any next step would need to show clear practical value before deeper commitment."
        )

    if "risk_sensitivity" in detected_signals:
        sentences.append(
            "Risk, reliability, and operational impact would need to be addressed explicitly."
        )

    if "skepticism" in detected_signals:
        sentences.append(
            "I would want the case framed in concrete terms rather than broad claims."
        )

    if not sentences and priorities:
        sentences.append(f"My current priority is {priorities[0]}.")
    elif not sentences and pains:
        sentences.append(f"One of the main constraints on my side is {pains[0]}.")
    elif not sentences and goals:
        sentences.append(f"The relevant objective for me is {goals[0]}.")
    elif not sentences and blockers:
        sentences.append(f"A likely blocker is {blockers[0]}.")
    elif not sentences:
        if persona.communication_style == SimulatedPersona.CommunicationStyle.DIRECT:
            sentences.append("I prefer a practical and concrete discussion.")
        else:
            sentences.append("I would evaluate this on practical fit, timing, and internal feasibility.")

    if persona.communication_style == SimulatedPersona.CommunicationStyle.CONCISE:
        return " ".join(sentences[:1])
    return " ".join(sentences[:2])


def _build_next_step(persona: SimulatedPersona, detected_signals: list[str]) -> str:
    decision_frame = persona.decision_frame
    trust = Decimal(persona.trust_level)
    frustration = Decimal(persona.frustration_level)
    urgency = Decimal(persona.urgency_level)

    if "rejection" in detected_signals:
        return "At this stage, I would leave it here rather than push the conversation further."

    if frustration >= Decimal("0.60"):
        return "If you want to continue, keep the next message brief and highly specific."

    if "meeting_request" in detected_signals or urgency >= Decimal("0.60"):
        if decision_frame in {
            SimulatedPersona.DecisionFrame.COMMITTEE,
            SimulatedPersona.DecisionFrame.PROCUREMENT,
            SimulatedPersona.DecisionFrame.MANAGER_REVIEW,
        }:
            return "A short initial discussion is fine, but I would still need something concise that I can circulate internally."
        return "A short call would be a reasonable next step."

    if trust >= Decimal("0.55"):
        return "The most useful next step would be a concise outline with concrete scope, assumptions, and expected value."

    return "The best next step would be a short, concrete explanation of what you are proposing and why it is relevant here."


def _build_signoff(persona: SimulatedPersona) -> str:
    if Decimal(persona.formality) >= Decimal("0.75"):
        return f"Best regards,\n{persona.full_name}"
    return f"Best,\n{persona.first_name or persona.full_name}"


def _persist_interaction_memory(
    *,
    persona: SimulatedPersona,
    incoming_message: SimulatedIncomingMessage,
    detected_signals: list[str],
) -> bool:
    content = (
        f"Subject: {incoming_message.subject or '(no subject)'}\n"
        f"Signals: {', '.join(detected_signals)}\n"
        f"Sender: {incoming_message.sender_name or incoming_message.sender_email or 'unknown'}\n"
        f"Body excerpt: {_excerpt(incoming_message.body, 280)}"
    )

    memory, created = SimulatedPersonaMemory.objects.get_or_create(
        persona=persona,
        kind=_memory_kind_for_signals(detected_signals),
        title=_memory_title_for_message(incoming_message),
        defaults={
            "content": content,
            "salience": _memory_salience_for_signals(detected_signals),
            "source": "smll_engine_v0",
            "is_active": True,
        },
    )

    if not created:
        memory.content = content
        memory.salience = _memory_salience_for_signals(detected_signals)
        memory.source = "smll_engine_v0"
        memory.is_active = True
        memory.save(update_fields=["content", "salience", "source", "is_active", "updated_at"])

    return created


def _memory_kind_for_signals(signals: list[str]) -> str:
    if "budget_pressure" in signals or "skepticism" in signals or "rejection" in signals:
        return SimulatedPersonaMemory.MemoryKind.OBJECTION
    if "positive_interest" in signals or "meeting_request" in signals:
        return SimulatedPersonaMemory.MemoryKind.RELATION
    return SimulatedPersonaMemory.MemoryKind.GENERAL


def _memory_salience_for_signals(signals: list[str]) -> Decimal:
    if "rejection" in signals:
        return Decimal("0.90")
    if "meeting_request" in signals:
        return Decimal("0.85")
    if "budget_pressure" in signals or "friction" in signals:
        return Decimal("0.80")
    if "positive_interest" in signals:
        return Decimal("0.75")
    return Decimal("0.55")


def _memory_title_for_message(incoming_message: SimulatedIncomingMessage) -> str:
    subject = (incoming_message.subject or "").strip()
    if subject:
        return f"Interaction: {subject[:120]}"
    return "Interaction: message without subject"


def _excerpt(text: str, max_length: int) -> str:
    normalized = " ".join((text or "").split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."
