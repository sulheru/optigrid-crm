from __future__ import annotations

import itertools
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services.approval import approve_external_action_intent
from apps.external_actions.services.dispatcher import dispatch_external_action_intent


_COUNTER = itertools.count(1)


def _next(prefix: str) -> str:
    return f"{prefix}-{next(_COUNTER)}"


def _model_fields():
    return {f.name for f in ExternalActionIntent._meta.fields}


def _has(field):
    return field in _model_fields()


def _build_instance(model_class, overrides=None, depth: int = 0):
    overrides = overrides or {}

    if depth > 3:
        raise RuntimeError("Recursion")

    if model_class is get_user_model():
        return model_class.objects.create_user(
            username=_next("user"),
            email=f"{_next('mail')}@test.com",
            password="test"
        )

    data = {}
    for f in model_class._meta.fields:
        if f.auto_created or f.primary_key:
            continue
        if f.name in overrides:
            data[f.name] = overrides[f.name]
            continue
        if f.has_default():
            continue
        if f.null:
            continue

        if isinstance(f, models.ForeignKey):
            data[f.name] = _build_instance(f.remote_field.model, depth=depth+1)
        elif isinstance(f, models.CharField):
            data[f.name] = _next(f.name)
        elif isinstance(f, models.BooleanField):
            data[f.name] = False
        else:
            data[f.name] = 1

    data.update(overrides)
    return model_class.objects.create(**data)


def build_intent(**kw):
    return _build_instance(ExternalActionIntent, kw)


class ExternalActionDispatcherTests(TestCase):

    def test_dispatch_requires_approval_when_flagged(self):
        intent = build_intent(approval_required=True)
        with self.assertRaises(ValueError):
            dispatch_external_action_intent(intent)

    def test_dispatch_executes_when_approved(self):
        intent = build_intent(approval_required=True)
        user = _build_instance(get_user_model())

        approve_external_action_intent(intent, user)

        result = dispatch_external_action_intent(intent)
        result.refresh_from_db()

        if _has("execution_status"):
            self.assertNotEqual(result.execution_status, "draft")

    def test_dispatch_executes_without_approval(self):
        intent = build_intent(approval_required=False)

        result = dispatch_external_action_intent(intent)
        result.refresh_from_db()

        if _has("execution_status"):
            self.assertNotEqual(result.execution_status, "draft")

    def test_dispatch_idempotent(self):
        intent = build_intent(approval_required=False)

        with patch("apps.external_actions.services.dispatcher.send_email_draft") as m:
            m.return_value = {"ok": True}

            dispatch_external_action_intent(intent)
            dispatch_external_action_intent(intent)

            self.assertEqual(m.call_count, 1)

    def test_dispatch_failure_sets_error(self):
        intent = build_intent(approval_required=False)

        with patch(
            "apps.external_actions.services.dispatcher.send_email_draft",
            side_effect=RuntimeError("fail")
        ):
            with self.assertRaises(RuntimeError):
                dispatch_external_action_intent(intent)

        intent.refresh_from_db()

        if _has("execution_status"):
            self.assertNotEqual(intent.execution_status, "draft")

        if _has("error_message"):
            self.assertEqual(intent.error_message, "fail")
