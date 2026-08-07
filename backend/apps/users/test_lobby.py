"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-21-authorization-lobby]] · [[adr-16-m365-graph]]
Docs: [[BACKEND]] · [[AUTH]] · [[API]]
LIVE-DOC:END"""

"""adr-21 rule 1: every gated route requires a Django session AND at least
one Group, except the lobby. `test_rbac.py`/`test_auth.py` prove this only
incidentally, per view. This enumerates the URLconf and asserts the general
rule holds for every route it finds — a newly-added gated route with no
Group check fails this test even if no other test names it."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import get_resolver
from django.urls.resolvers import URLResolver

pytestmark = pytest.mark.django_db

User = get_user_model()

# adr-21 rule 1 named exceptions, plus the pre-existing carve-outs it names
# as outside the gate: `/accounts/*` (auth entry itself), health, the two
# bounded AllowAny m365 demo routes (adr-16 rule 3), and `/api/me/` — which
# adr-21 rule 4 itself relies on being readable pre-grant (the `groups`
# field is how a role-less session learns a grant landed). Django admin is
# excluded: it self-gates on `is_staff`, a separate mechanism from the
# Group-based RBAC this rule states ([[adr-14-auth]] rule 8).
EXEMPT_PREFIXES = ("admin/", "accounts/")
EXEMPT_PATHS = {"api/health/", "api/me/", "api/m365/hello/", "api/m365/world/"}


def _leaf_paths(patterns, prefix=""):
    paths = []
    for entry in patterns:
        if isinstance(entry, URLResolver):
            paths.extend(_leaf_paths(entry.url_patterns, prefix + str(entry.pattern)))
        else:
            pattern = prefix + str(entry.pattern)
            if "<" not in pattern and "(?P" not in pattern:
                paths.append(pattern)
    return paths


def _gated_paths():
    all_paths = _leaf_paths(get_resolver().url_patterns)
    gated = []
    for path in all_paths:
        if any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES):
            continue
        if path in EXEMPT_PATHS:
            continue
        gated.append(path)
    return sorted(set(gated))


def _roleless_user():
    return User.objects.create_user(sub="sub-lobby-roleless", email="lobby@example.com")


def test_gated_route_set_is_non_empty():
    # Sanity: this repo ships at least one Group-gated route today, so an
    # empty enumeration would silently pass this whole test file for the
    # wrong reason (an urlconf-walking bug, not a compliant app).
    assert _gated_paths()


@pytest.mark.parametrize("path", _gated_paths())
def test_roleless_authenticated_user_is_refused_every_gated_route(client, path):
    client.force_login(_roleless_user())
    response = client.get("/" + path)
    assert response.status_code == 403, (
        f"/{path} admitted a role-less authenticated session; adr-21 rule 1 "
        "requires Group membership for every route outside the lobby."
    )


@pytest.mark.parametrize("path", sorted(EXEMPT_PATHS))
def test_named_exceptions_do_not_reject_for_lack_of_group(client, path):
    client.force_login(_roleless_user())
    response = client.get("/" + path)
    assert response.status_code != 403
