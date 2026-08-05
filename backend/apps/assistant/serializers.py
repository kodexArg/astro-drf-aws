"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-25-page-context-assistant]] · [[adr-18-async-mandatory]] · [[adr-07-api-and-backend]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

"""Serializers for POST /api/assistant/ask/ ([[adr-25-page-context-assistant]])."""

from rest_framework import serializers

from apps.users.serializers import DEFAULT_PAGE_CHOICES

# Blank default_page is not a page identity the assistant can anchor on.
PAGE_CHOICES = sorted(p for p in DEFAULT_PAGE_CHOICES if p)


class AskRequestSerializer(serializers.Serializer):
    utterance = serializers.CharField(allow_blank=False, trim_whitespace=True)
    page = serializers.ChoiceField(choices=[(p, p) for p in PAGE_CHOICES])


class AssistantLinkSerializer(serializers.Serializer):
    target = serializers.CharField()
    label = serializers.CharField()
