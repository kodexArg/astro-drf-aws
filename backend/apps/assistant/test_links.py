"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
Governed by: [[adr-24-page-context-assistant]] · [[adr-16-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""Unit tests for filter_registry_links."""

from apps.assistant.links import filter_registry_links


def test_drops_out_of_registry_targets():
    result = filter_registry_links(
        [
            {"target": "/chatui/", "label": "Chat"},
            {"target": "https://evil.example/", "label": "Evil"},
            {"target": "/not-a-real-page/", "label": "Ghost"},
        ]
    )
    assert result == [{"target": "/chatui/", "label": "Chat"}]


def test_dedupes_by_target():
    result = filter_registry_links(
        [
            {"target": "/chatui/", "label": "A"},
            {"target": "/chatui/", "label": "B"},
        ]
    )
    assert result == [{"target": "/chatui/", "label": "A"}]


def test_empty_and_malformed():
    assert filter_registry_links(None) == []
    assert filter_registry_links([{"target": "/chatui/"}]) == []
    assert filter_registry_links("nope") == []
