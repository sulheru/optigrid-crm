from django.core.management.base import BaseCommand
from apps.updates.services_replay import replay_email


class Command(BaseCommand):
    help = "Replay rule engine for a given email"

    def add_arguments(self, parser):
        parser.add_argument("email_id", type=int)

    def handle(self, *args, **kwargs):
        email_id = kwargs["email_id"]

        proposals = replay_email(email_id)

        self.stdout.write(self.style.SUCCESS(f"Replay done: {proposals}"))
