---
title: adr-07-api-and-backend
type: adr
category: backend
use_case: adding or changing an endpoint, editing docs/API.md, writing a serializer, writing a viewset or model, touching backend settings
created: 2026-07-10
modified: 2026-08-04
tags: [adr, api, backend]
---

# ADR-07 — API and backend

## CONTEXT

> The backend zone is entered only through the API contract. No route
> exists in code without its row.

Rules only; content lives in [[API]] and [[BACKEND]].

## ASSERTIONS

1. An endpoint is valid if and only if it is declared in [[API]]. No route
   may exist in code without its row; an undeclared route found in code is a
   defect, regardless of whether it works.
2. [[API]] is written before tests and before models: `plan → [[API]] →
   [[TDD]] → models.py → rest of DRF`.
3. The change protocol of [[API]] is binding: a row changes in its own
   reviewable act; removing an endpoint removes its row first, the code
   second; a row change invalidates the corresponding [[TDD]] entry in the
   same cycle.
4. HTMX fragment routes are endpoints and follow rule 1 ([[HTMX]], ruled by
   [[adr-09-htmx]]).
5. Backend service rules are owned by [[BACKEND]]: single Django project,
   one app per domain, env-driven settings, viewsets by default, ASGI on
   port 8000.
6. All backend code is born through the [[TDD]] flow; the full loop is
   ruled by [[adr-11-development-flow]].
7. Every variable a setting reads is declared in [[VARIABLES]]; secrets come
   from AWS Secrets Manager only.

## RELATED

### related files

- [[adr-01-constitution]] — authority order this ADR sits beneath
- [[API]] — the endpoint contract
- [[BACKEND]] — Django/DRF service rules
- [[TDD]] — the test-first flow
- [[HTMX]] — fragment routes as endpoints
- [[VARIABLES]] — the variable inventory
- [[adr-09-htmx]] — HTMX fragment-route detail
- [[adr-11-development-flow]] — the full backend loop
