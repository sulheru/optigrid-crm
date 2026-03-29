from django.test import SimpleTestCase

from apps.providers.mail_runtime import resolve_mail_account


class MailRuntimeTests(SimpleTestCase):
    def test_resolve_default_account(self):
        account = resolve_mail_account()
        self.assertEqual(account.account_key, "default")
        self.assertEqual(account.provider, "embedded")
