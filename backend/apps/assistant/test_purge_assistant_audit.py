"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
Governed by: [[adr-24-page-context-assistant]] · [[adr-16-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""Tests for purge_assistant_audit management command."""

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.assistant.models import AssistantQuery

pytestmark = pytest.mark.django_db


def test_purge_deletes_only_old_rows(django_user_model, settings, capsys):
    settings.ASSISTANT_AUDIT_RETENTION_DAYS = 7
    user = django_user_model.objects.create(sub="purge-1", email="purge@example.com")
    old = AssistantQuery.objects.create(user=user, page="/chatui/", status="ok")
    recent = AssistantQuery.objects.create(user=user, page="/chatui/", status="ok")
    AssistantQuery.objects.filter(pk=old.pk).update(
        created_at=timezone.now() - timedelta(days=10)
    )

    call_command("purge_assistant_audit")
    assert not AssistantQuery.objects.filter(pk=old.pk).exists()
    assert AssistantQuery.objects.filter(pk=recent.pk).exists()


def test_purge_dry_run_does_not_delete(django_user_model, settings):
    settings.ASSISTANT_AUDIT_RETENTION_DAYS = 1
    user = django_user_model.objects.create(sub="purge-2", email="purge2@example.com")
    row = AssistantQuery.objects.create(user=user, page="/", status="ok")
    AssistantQuery.objects.filter(pk=row.pk).update(
        created_at=timezone.now() - timedelta(days=5)
    )
    call_command("purge_assistant_audit", "--dry-run")
    assert AssistantQuery.objects.filter(pk=row.pk).exists()
