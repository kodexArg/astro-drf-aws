---
title: adr-11-development-flow
type: adr
category: project
use_case: starting any user-facing work, entering the backend zone, deciding whether the API already solves a need, closing a feature loop
created: 2026-07-10
modified: 2026-08-04
tags: [adr, development-flow, bdd, tdd, api]
---

# ADR-11 — the development flow

## CONTEXT

> User-facing work is bound by the BDD gate; the backend zone is entered
> only through the API contract. This ADR makes that order invariant.

Rules only. This ADR gives force to the loop defined in
[[DEVELOPMENT-LOOP]] and indexed in [[AGENTS]]; that same file carries its
operational rendering — the sequence and the tool/skill at each step.

## ASSERTIONS

1. User-facing work is bound by the [[BDD]] gate: its [[BDD]] entry exists
   before its code does.
2. The backend zone is entered only through [[API]], and a need is served
   by an endpoint already declared there before a new one is considered.
3. A new endpoint's row lands in [[API]] before its code, and the code that
   follows is born through the [[TDD]] flow ([[adr-07-api-and-backend]]).
4. The backend zone is exited only through the checkpoint — does [[API]]
   solve the need? Its rendering as a loop lives in [[DEVELOPMENT-LOOP]].
5. What this ADR makes invariant is the order of the gates: [[BDD]] before
   code, [[API]] before backend work, the checkpoint before leaving the
   backend zone. The intermediate steps are owned by [[BDD]], [[TDD]], and
   the stack docs.
6. Every feature enters through this loop; each gate ([[BDD]], [[API]],
   [[TDD]]) binds now, wherever its subject exists, including the
   template's own construction.

## RELATED

### related files

- [[adr-01-constitution]] — authority order this ADR sits beneath
- [[adr-07-api-and-backend]] — the backend-zone entry contract
- [[BDD]] — user-facing gate
- [[TDD]] — backend test-first flow
- [[API]] — the contract entered and exited
- [[DEVELOPMENT-LOOP]] — the operational rendering
- [[AGENTS]] — where this loop is indexed
