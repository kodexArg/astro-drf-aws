"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-25-page-context-assistant]] · [[adr-18-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""Server-side validation of assistant link suggestions against the nav registry.

A target outside the closed page set is dropped — never repaired, never parsed
from prose ([[adr-25-page-context-assistant]] rule 4).
"""

from apps.users.serializers import DEFAULT_PAGE_CHOICES

_ALLOWED_TARGETS = frozenset(p for p in DEFAULT_PAGE_CHOICES if p)


def filter_registry_links(candidates):
    """Return only `{target, label}` entries whose target is in the nav registry."""
    if not candidates:
        return []
    out = []
    seen = set()
    for item in candidates:
        if not isinstance(item, dict):
            continue
        target = item.get("target")
        label = item.get("label")
        if not isinstance(target, str) or not isinstance(label, str):
            continue
        target = target.strip()
        label = label.strip()
        if not target or not label or target not in _ALLOWED_TARGETS:
            continue
        if target in seen:
            continue
        seen.add(target)
        out.append({"target": target, "label": label})
    return out
