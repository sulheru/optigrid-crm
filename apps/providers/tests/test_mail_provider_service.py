from django.test import SimpleTestCase

from apps.emailing.services.mail_provider_service import prepare_provider_draft


class MailProviderServiceTests(SimpleTestCase):
    def test_prepare_provider_draft_returns_provider_context(self):
        result = prepare_provider_draft(
            subject="Hello",
            body_text="World",
            to=["test@example.com"],
        )
        self.assertEqual(result["provider"], "embedded")
        self.assertEqual(result["provider_status"], "draft_created")
