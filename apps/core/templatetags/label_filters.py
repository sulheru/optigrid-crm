from django import template

from apps.core.labels import (
    ACTION_TYPE_LABELS,
    EMAIL_TYPE_LABELS,
    INTENT_LABELS,
    RECOMMENDATION_LABELS,
    REPLY_TYPE_LABELS,
    RISK_FLAG_LABELS,
    STAGE_LABELS,
    STATUS_LABELS,
)

register = template.Library()


def _fallback(value):
    if value is None:
        return ""
    return str(value).replace("_", " ").strip().title()


@register.filter(name="recommendation_label")
def recommendation_label(value):
    return RECOMMENDATION_LABELS.get(value, _fallback(value))


@register.filter(name="email_type_label")
def email_type_label(value):
    return EMAIL_TYPE_LABELS.get(value, _fallback(value))


@register.filter(name="reply_label")
def reply_label(value):
    return REPLY_TYPE_LABELS.get(value, _fallback(value))


@register.filter(name="action_label")
def action_label(value):
    return ACTION_TYPE_LABELS.get(value, _fallback(value))


@register.filter(name="status_label")
def status_label(value):
    return STATUS_LABELS.get(value, _fallback(value))


@register.filter(name="stage_label")
def stage_label(value):
    return STAGE_LABELS.get(value, _fallback(value))


@register.filter(name="intent_label")
def intent_label(value):
    return INTENT_LABELS.get(value, _fallback(value))


@register.filter(name="risk_flag_label")
def risk_flag_label(value):
    return RISK_FLAG_LABELS.get(value, _fallback(value))
