from django.test import SimpleTestCase

from apps.external_actions.dispatcher import dispatch_external_action_intent
from apps.external_actions.services import (
    approve_external_action_intent,
    dispatch_external_action_intent as service_dispatch_external_action_intent,
)


class ExternalActionsImportTests(SimpleTestCase):
    def test_dispatcher_shim_points_to_service_dispatcher(self):
        self.assertIs(dispatch_external_action_intent, service_dispatch_external_action_intent)

    def test_services_exports_are_available(self):
        self.assertTrue(callable(approve_external_action_intent))
        self.assertTrue(callable(service_dispatch_external_action_intent))
