---
title: TDD
type: reference
status: active
created: 2026-07-10
tags: [harness, tdd, backend, assertions]
---

# TDD — the test-first method, and the instruction manual for `docs/tdds/`

## The assertion method: tests first, code second, the assertion stays

This document is also the working method the
[[assertion-00-discipline|assertion family]] shares whenever an assertion's
law is unmet. **Tests first. Code second. The assertion stays.**

An assertion is a law. The tests linked from its `## RELATED` section are
how the project answers that law; the implementation is what makes those
tests pass. Order is not optional:

1. Interpret the assertion until every concrete rule is named (latency
   bound, click depth, query shape, header value, group membership, …).
2. Write or demand the **failing** tests that encode those rules — one
   assertion may need more than one test; every rule the paragraph states
   must be covered.
3. Link those tests under the assertion's `### Tests` chapter before
   treating the batch as ready for implementation.
4. Implement the fix or feature until the tests pass.
5. Leave the tests in the tree. They are the permanent check that the law
   still holds — not a scaffold deleted after green.

A link under `### Tests` counts only if it can actually be run and the run
**demonstrates** the assertion's rules — a README bullet, a manual
checklist, or a code comment is not a proving test. If the only evidence is
prose, the assertion is unmet. Set `verified` to today only after actually
running the linked tests and watching them pass ([[assertion-00-discipline]]).

This is the same flow the backend manual below already prescribes for
`docs/tdds/` — an assertion's proving test is simply another kind of TDD
entry, born the same way: failing test first, implementation second.

## `docs/tdds/` — instruction manual for backend TDD entries

> [!note] Active
> Every new backend piece is born here, wherever its subject exists ([[adr-11-development-flow]] r6). The template ships no `tdd-NN` entries; a project creates its own under `docs/tdds/`.

## Scope

> [!important] Backend only
> The TDD flow covers Django/DRF code exclusively. Frontend testing is owned by [[FRONTEND]] and is explicitly excluded from this flow.

## Purpose

From activation onward, every new piece of backend code is **born here**. `docs/tdds/` is where backend code generation starts — never directly in the code. No model, endpoint, service, or command exists before its TDD entry does.

## The flow

1. An approved [[API]] row exists (the contract comes first).
2. Create `docs/tdds/tdd-NN-slug.md` — sequential `NN`, kebab-case slug — following the section layout described below.
3. Write the failing tests the entry lists. Run them; they must fail.
4. Write `models.py` changes.
5. Implement until green.
6. Mark the entry `done`.

## Entry frontmatter contract

Every entry carries:

```yaml
title: tdd-NN-slug
type: tdd
status: draft | red | green | done
created: YYYY-MM-DD
api: []        # list of the [[API]] rows/paths this entry covers
tags: [tdd]
```

Status transitions:

- `draft` — entry written, tests not yet coded.
- `red` — tests exist and fail; implementation may begin.
- `green` — implementation passes every listed test.
- `done` — implementation notes filled; entry closed.

> [!note] One entry, one coherent piece
> An entry covers a single coherent unit of code: a model plus its endpoints, a service, a management command. Entries are small. If an entry needs a plural of concerns, split it.

## Entry layout

Every entry follows the frontmatter contract and flow above; a project's first entry sets the section layout that the rest reuse. Do not invent divergent layouts.

## Relationship to BDD

Features arriving from users enter via [[BDD]] first. The backend half of a BDD entry lands here as one or more TDD entries; link the originating BDD entry from each.
