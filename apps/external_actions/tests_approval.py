from __future__ import annotations

import itertools

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services.approval import approve_external_action_intent


_COUNTER = itertools.count(1)


def _next(prefix: str) -> str:
    return f"{prefix}-{next(_COUNTER)}"


def _build_instance(model_class, overrides=None, depth: int = 0):
    overrides = overrides or {}

    if depth > 3:
        raise RuntimeError(f"Demasiada recursión creando {model_class.__name__}")

    if model_class is get_user_model():
        username = overrides.pop("username", _next("user"))
        email = overrides.pop("email", f"{username}@example.com")
        password = overrides.pop("password", "testpass123")
        return model_class.objects.create_user(username=username, email=email, password=password, **overrides)

    data = {}
    for field in model_class._meta.fields:
        if getattr(field, "auto_created", False):
            continue
        if field.name in overrides:
            data[field.name] = overrides[field.name]
            continue
        if getattr(field, "primary_key", False):
            continue
        if getattr(field, "has_default", lambda: False)():
            continue
        if getattr(field, "null", False):
            continue
        if getattr(field, "blank", False) and not isinstance(field, models.ForeignKey):
            continue

        if isinstance(field, models.ForeignKey):
            related_model = field.remote_field.model
            data[field.name] = _build_instance(related_model, depth=depth + 1)
        elif isinstance(field, models.CharField):
            data[field.name] = _next(field.name)
        elif isinstance(field, models.TextField):
            data[field.name] = _next(field.name)
        elif isinstance(field, models.BooleanField):
            data[field.name] = False
        elif isinstance(field, models.IntegerField):
            data[field.name] = 1
        elif isinstance(field, models.FloatField):
            data[field.name] = 1.0
        elif isinstance(field, models.DecimalField):
            data[field.name] = "1.00"
        else:
            raise RuntimeError(
                f"No sé cómo construir automáticamente el campo {model_class.__name__}.{field.name} ({field.__class__.__name__})"
            )

    data.update(overrides)
    return model_class.objects.create(**data)


def build_external_action_intent(**overrides) -> ExternalActionIntent:
    return _build_instance(ExternalActionIntent, overrides=overrides)


class ExternalActionApprovalTests(TestCase):
    def test_cannot_approve_when_approval_not_required(self):
        intent = build_external_action_intent(approval_required=False)
        user = _build_instance(get_user_model())

        with self.assertRaisesMessage(ValueError, "Este intent no requiere aprobación"):
            approve_external_action_intent(intent, user)

    def test_approve_persists_user_and_timestamp(self):
        intent = build_external_action_intent(
            approval_required=True,
            approval_status=getattr(getattr(ExternalActionIntent, "ApprovalStatus", object), "PENDING", "pending"),
        )
        user = _build_instance(get_user_model())

        approved = approve_external_action_intent(intent, user)
        approved.refresh_from_db()

        approved_value = getattr(getattr(ExternalActionIntent, "ApprovalStatus", object), "APPROVED", "approved")

        self.assertEqual(approved.approval_status, approved_value)
        self.assertEqual(approved.approved_by_id, user.id)
        self.assertIsNotNone(approved.approved_at)
