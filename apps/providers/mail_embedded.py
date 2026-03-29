from __future__ import annotations

from apps.providers.mail_provider import DraftEnvelope, MailAccountRef, ProviderDraftResult


class EmbeddedMailProvider:
    provider_key = "embedded"

    def create_draft(self, *, account: MailAccountRef, envelope: DraftEnvelope) -> ProviderDraftResult:
        return ProviderDraftResult(
            provider=self.provider_key,
            account_key=account.account_key,
            external_draft_id=None,
            status="draft_created",
            payload={
                "mode": "local_embedded",
                "mailbox": account.mailbox,
                "subject": envelope.subject,
                "to": envelope.to,
            },
        )
