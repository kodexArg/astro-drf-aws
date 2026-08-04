---
title: adr-22-bootstrap-allowlist-grant
type: adr
category: backend
use_case: configuring AUTH_BOOTSTRAP_ALLOWLIST, deploying an environment that needs a pre-granted role, reviewing the login provisioning path
created: 2026-07-10
modified: 2026-08-04
tags: [adr, auth, bootstrap, allowlist]
---

# ADR-22 — the bootstrap allowlist grant

## CONTEXT

> A second, bounded grant path: an env-driven allowlist that pre-fills the
> same `AccessRequest.role` an admin would otherwise set by hand.

Rules only; content lives in [[AUTH]], [[VARIABLES]], [[GLOSSARY]]. This ADR
adds a named exception to [[adr-21-authorization-lobby]] rule 3; it
supersedes nothing and narrows nothing else.

## ASSERTIONS

1. A second, bounded grant path exists: the env-driven bootstrap allowlist.
   `AUTH_BOOTSTRAP_ALLOWLIST` ([[GLOSSARY]], [[VARIABLES]]) names accounts
   whose `AccessRequest.role` is filled automatically in the shared login
   provisioning path, at first login and re-checked on every login. This is
   the exact precedent of the bootstrap superuser ([[adr-14-auth]] rule 8):
   an operator/deploy-time, owner-controlled exception — never self-service,
   since the requesting user cannot influence the value ([[AUTH]]).
2. The allowlist reuses the existing machinery and creates no parallel
   authority. It only pre-fills the same `AccessRequest.role` an admin
   would set by hand in `/admin/`; the `post_save` signal of
   [[adr-21-authorization-lobby]] rule 3 remains the sole path from the row
   to a Group membership, and enforcement still reads Django Groups only
   ([[adr-14-auth]] rules 1–2, unchanged).
3. The allowlist never overrides an admin. It fills `role` only while `role`
   is null; a role already granted — or later cleared and re-granted —
   through `/admin/` is authoritative. A pair naming a Group that does not
   exist is skipped with a logged warning: a config typo must never break
   login or mint a new Group.
4. Accounts arrive only through env/[[VARIABLES]], never through code. The
   variable's row enters [[VARIABLES]] before code reads it and its name
   enters [[GLOSSARY]] before first use. The committed `.env.example` may
   carry only the local-dev seed (`dev@example.com`); real accounts live in
   each project's django secret. Hardcoding an account identifier anywhere
   in code or docs is a defect ([[PRD]] — the template stays
   account-agnostic).
5. This is a doctrine addition, not a reversal. Cognito remains
   authentication-only, RBAC remains exclusively Django Groups, the lobby
   boundary of [[adr-21-authorization-lobby]] rules 1–2 is untouched, and the
   bootstrap superuser exception is neither widened nor connected to this
   one.

## RELATED

### related files

- [[adr-14-auth]] — the bootstrap-superuser precedent (rule 8)
- [[adr-21-authorization-lobby]] — the `post_save` signal this allowlist
  feeds (rule 3)
- [[AUTH]] — allowlist mechanics
- [[VARIABLES]] — `AUTH_BOOTSTRAP_ALLOWLIST` row
- [[GLOSSARY]] — the variable's name and `role`/`AccessRequest` terms
- [[PRD]] — account-agnostic template requirement
