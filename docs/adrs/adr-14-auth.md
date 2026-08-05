---
title: adr-14-auth
type: adr
category: backend
use_case: touching authentication or session handling, adding a route under /accounts/, writing a permission class, working with Cognito or the bootstrap superuser
created: 2026-07-10
modified: 2026-08-04
tags: [adr, auth, cognito]
---

# ADR-14 — authentication

## CONTEXT

> Cognito authenticates only; all authorization and RBAC live in Django
> Groups.

Rules only; content lives in [[AUTH]].

## ASSERTIONS

1. AWS Cognito is the only authentication provider, and it authenticates
   ONLY. No second IdP and no home-grown password authentication in
   production. The OIDC flow is owned by [[AUTH]].
2. All authorization and RBAC live in Django — never in Cognito. Roles are
   Django Groups enforced by DRF permission classes ([[BACKEND]]). Cognito
   groups and custom-claims-as-roles are prohibited; a permission decision
   read from a Cognito token is a defect.
3. After token verification Django establishes its own session. Browser
   auth is Django session auth backed by the database ([[CACHE]], no Redis)
   because HTMX requires it ([[HTMX]]); token-only SPA auth is not the
   default.
4. The `/accounts/` prefix is the entire auth surface. The ALB routes it to
   the backend ([[INFRASTRUCTURE]]); every `/accounts/` route is declared in
   [[API]] before code exists — no shadow routes ([[adr-07-api-and-backend]]).
5. User rows key on the Cognito `sub` claim; profile fields mirror Cognito
   standard attributes ([[GLOSSARY]], [[BD]]).
6. A DEBUG-only development auth path MUST exist and MUST produce the same
   Django user model and session mechanics as the real flow. It is guarded
   so it cannot run in production by a deploy-time system check that
   hard-fails — not by convention ([[AUTH]]).
7. Cognito configuration is declared in [[VARIABLES]] first and sourced only
   from Secrets Manager `alvs/<env>/<project>/cognito`. The frontend
   receives ZERO Cognito variables and ZERO secrets ([[INFRASTRUCTURE]]).
8. Named exception, bounded to one account (owner override, 2026-07-14,
   issue #108): the bootstrap superuser — the single row keyed
   `sub=bootstrap-admin`, created/rotated only by the `bootstrap_admin`
   management command from `DJANGO_SUPERUSER_EMAIL`/`DJANGO_SUPERUSER_PASSWORD`
   ([[VARIABLES]], [[BACKEND]]) — is the only account permitted a usable
   password, exclusively for Django admin bootstrap/break-glass access at
   `/admin/` ([[API]]). Every other account keeps `set_unusable_password`
   and rule 1 stands untouched: no second IdP, no password path on
   `/accounts/`, and this exception widens nothing else.
## RELATED

### related files

- [[adr-05-glossary-and-localisation]] — naming gate for auth terms
- [[adr-07-api-and-backend]] — `/accounts/*` routes declared in API
- [[adr-16-m365-graph]] — the bounded `AllowAny` exception, referenced by
  [[adr-21-authorization-lobby]]
- [[adr-21-authorization-lobby]] — the lobby: RBAC gate beyond authentication
- [[adr-22-bootstrap-allowlist-grant]] — the env-driven grant precedent this
  ADR's rule 8 set
- [[AUTH]] — the full OIDC/session mechanics
- [[BACKEND]] — Django permission classes
- [[HTMX]] — why session auth is required
- [[INFRASTRUCTURE]] — ALB routing and secrets scoping
- [[GLOSSARY]], [[VARIABLES]], [[BD]] — naming, env, and DB detail
