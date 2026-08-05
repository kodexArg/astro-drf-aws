"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-17-chatbot-two-tier]] · [[adr-18-async-mandatory]] · [[adr-07-api-and-backend]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

"""Serializers for the chatbot router choosing tier ([[adr-17-chatbot-two-tier]]).

`RouteRequestSerializer` validates the inbound utterance. `ActionSerializer`
is a strict output whitelist — `kind`, `target`, `label` only — enforcing
rule 5 (no free-prose restatement) at the response boundary, not just by
convention in the view.
"""

from rest_framework import serializers


class RouteRequestSerializer(serializers.Serializer):
    utterance = serializers.CharField(allow_blank=False, trim_whitespace=True)


class ActionSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=["navigate", "confirm"])
    target = serializers.CharField(allow_null=True, required=False)
    label = serializers.CharField()
