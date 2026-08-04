---
title: assertion-02-group-gated-rbac
type: reference
status: active
created: 2026-08-04
verified: 2026-08-04
tags: [assertion, backend, auth, rbac]
---

# Assertion-02 — a role-less session is confined, and only Django Groups decide

An authenticated Django session carrying zero Django Group memberships MUST
be rejected (403) by any view gated on Group membership, regardless of
whatever claim the identity provider itself carried — a `cognito:groups`
claim naming a Group MUST NEVER grant access on its own. Authorization is
decided exclusively by reading Django Groups, never a Cognito claim
([[adr-14-auth]] rule 2, [[adr-21-authorization-lobby]] rule 1).

## RELATED

### Tests

- [test_rbac.py::test_restricted_403_for_non_member](../../backend/apps/users/test_rbac.py) —
  an authenticated user with no Group membership gets 403 from the
  Group-gated `/api/restricted/` view.
- [test_rbac.py::test_permission_reads_only_django_groups](../../backend/apps/users/test_rbac.py) —
  a user upserted from claims carrying a hostile `cognito:groups: [admins]`
  claim gains zero real Django Groups and is still rejected with 403.

Both run and pass as of 2026-08-04 (`uv run pytest apps/users/test_rbac.py`
against a live local Postgres via `docker compose up -d db`; 20 passed).

### Files

- [backend/apps/users/permissions.py](../../backend/apps/users/permissions.py)
- [backend/apps/users/views.py](../../backend/apps/users/views.py)

### Docs

- [[adr-14-auth]]
- [[adr-21-authorization-lobby]]
- [[AUTH]]
