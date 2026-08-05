"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-25-page-context-assistant]] · [[adr-18-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""`manage.py purge_assistant_audit [--dry-run]`."""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.assistant.models import AssistantQuery


class Command(BaseCommand):
    help = "Delete AssistantQuery audit rows older than ASSISTANT_AUDIT_RETENTION_DAYS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="report the count that would be deleted without deleting",
        )

    def handle(self, *args, **options):
        retention_days = settings.ASSISTANT_AUDIT_RETENTION_DAYS
        cutoff = timezone.now() - timezone.timedelta(days=retention_days)
        queryset = AssistantQuery.objects.filter(created_at__lt=cutoff)
        count = queryset.count()

        if options["dry_run"]:
            self.stdout.write(
                f"dry-run: {count} row(s) older than {retention_days} day(s) would be deleted"
            )
            return

        queryset.delete()
        self.stdout.write(f"deleted {count} row(s) older than {retention_days} day(s)")
