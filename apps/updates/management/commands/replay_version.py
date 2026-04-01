from django.core.management.base import BaseCommand
from apps.updates.services_replay import replay_with_version


class Command(BaseCommand):
    help = "Replay with specific rules version"

    def add_arguments(self, parser):
        parser.add_argument("email_id", type=int)
        parser.add_argument("version", type=str)

    def handle(self, *args, **kwargs):
        result = replay_with_version(
            kwargs["email_id"],
            kwargs["version"],
        )

        self.stdout.write(self.style.SUCCESS(str(result)))
