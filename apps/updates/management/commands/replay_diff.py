from django.core.management.base import BaseCommand
from apps.updates.services_replay import replay_with_diff


class Command(BaseCommand):
    help = "Replay with diff"

    def add_arguments(self, parser):
        parser.add_argument("email_id", type=int)

    def handle(self, *args, **kwargs):
        result = replay_with_diff(kwargs["email_id"])

        self.stdout.write(self.style.SUCCESS(str(result)))
