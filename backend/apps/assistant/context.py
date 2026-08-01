"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
Governed by: [[adr-24-page-context-assistant]] · [[adr-16-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""Server-side page-context assembly for the assistant ([[adr-24-page-context-assistant]] rule 3).

The request carries a page identity only. v1 returns that path plus the
caller's Django group names — never client page text. Page-specific
recompute adapters may deepen this bag later without changing the wire
shape.
"""


def assemble_page_context(user, page):
    """Build a JSON-serializable context bag under the caller's Groups."""
    groups = sorted(user.groups.values_list("name", flat=True))
    return {
        "page": page,
        "groups": groups,
        "figures": {},
    }
