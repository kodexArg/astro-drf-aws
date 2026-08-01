"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
Governed by: [[adr-24-page-context-assistant]] · [[adr-16-async-mandatory]] · [[adr-03-api-and-backend]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

"""Models for the page-context assistant generating tier (adr-24-page-context-assistant).

`AssistantQuery` is one audit row per ask — utterance, page identity, answer,
model id, latency, user — under the same bounded retention as `IntentQuery`
([[CHATBOT]] — Retention).
"""

from django.conf import settings
from django.db import models


class AssistantQuery(models.Model):
    """One audit row per ask ([[CHATBOT]] — Retention)."""

    utterance = models.TextField(null=True, blank=True)
    page = models.CharField(max_length=255, blank=True, default="")
    answer = models.TextField(null=True, blank=True)
    raw_model_output = models.TextField(null=True, blank=True)
    links = models.JSONField(default=list)
    status = models.CharField(max_length=64, blank=True, default="")
    model_id = models.CharField(max_length=255, blank=True)
    latency_ms = models.FloatField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "pk"]

    def __str__(self):
        return f"{self.user_id}:{self.page}:{self.status or 'ok'}"
