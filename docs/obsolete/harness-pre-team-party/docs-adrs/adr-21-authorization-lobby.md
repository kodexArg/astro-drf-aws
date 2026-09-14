---
title: adr-21-authorization-lobby
type: adr
category: backend
use_case: adding a gated route, deciding what a role-less session may reach, writing the AccessRequest post_save signal
created: 2026-07-10
modified: 2026-08-04
tags: [adr, auth, lobby, rbac]
---

# ADR-21 — the authorization lobby

## CONTEXT

> `/` is the lobby: the sole route admitting both an anonymous visitor and a
> role-less authenticated session. Every other gated route requires a Group.

Rules only; content lives in [[AUTH]], [[GLOSSARY]], [[API]]. This ADR adds
to [[adr-14-auth]]; it narrows nothing that ADR states.

## ASSERTIONS

1. Every route requiring authentication requires an authenticated Django
   session AND membership in at least one Django Group, except `/`. A
   session authenticated by Cognito but carrying zero Group memberships is
   confined to `/` (the lobby) until that changes — RBAC stays Django
   Groups, decided in Django, never a Cognito claim ([[adr-14-auth]] rules
   1–2). Routes that already declare no authentication at all are outside
   this gate, not relaxations of it: the `AllowAny` named exception of
   [[adr-16-m365-graph]] rule 3 and the pre-existing `/accounts/*` and
   health routes.
2. `/` is the lobby — the sole route that admits both an anonymous visitor
   and a role-less authenticated session into the app's gated surface. No
   other route may ever relax rule 1 to admit a role-less user; a second
   such route is a widening of this boundary and requires a new ADR, never
   a local exception. The one standing exception is the bounded `AllowAny`
   carve-out of [[adr-16-m365-graph]] rule 3 — owner-directed and predating
   this ADR — which admits anonymous requests to two demo routes and is
   neither widened nor reopened here.
3. A role grant is an admin action, never self-service. A member of the
   `admins` role, working in Django admin (the existing `/admin/` mount,
   [[API]]), sets the `role` field ([[GLOSSARY]]) on the requesting user's
   `AccessRequest` row ([[GLOSSARY]]). A `post_save` signal on that write
   mirrors the non-null `role` into the user's Django Groups — the Group
   membership is what rule 1 checks, never the `AccessRequest` row itself.
   `AccessRequest` carries no authority until the signal runs; it is a
   record, not a permission.
4. Re-evaluation is per-request, riding the existing Django session — no
   token re-mint, no cache in the path. A page refresh after a grant is
   sufficient for the new Group membership to take effect on the next
   request, read through the already-declared `/api/me/` `groups` field
   ([[API]]) and Django's own Group-membership check. No caching layer sits
   between a grant and its enforcement ([[adr-10-cache]]).

## RELATED

### related files

- [[adr-14-auth]] — Cognito authentication, RBAC in Django, unchanged by
  this ADR
- [[adr-16-m365-graph]] — the bounded `AllowAny` exception referenced
- [[adr-22-bootstrap-allowlist-grant]] — a second, bounded grant path onto
  the same `AccessRequest.role` this ADR's rule 3 mirrors
- [[adr-10-cache]] — no caching layer between grant and enforcement (rule 4)
- [[AUTH]] — lobby mechanics
- [[API]] — `/api/me/` groups field
- [[GLOSSARY]] — `role`, `AccessRequest`, `lobby` terms
