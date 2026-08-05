---
name: assertion-review
description: >-
  Enforce assertion laws in docs/assertions/: interpret each law's concrete
  rules, resolve every RELATED link, confirm the Tests chapter actually
  proves the law via the tests-first method in docs/TDD.md, drive the fix
  or feature until the tests pass, then stamp verified to today's date. Use
  when reviewing docs/assertions/, adding an assertion, doing a periodic
  re-check, or when the owner asks to satisfy or audit an assertion.
---

# Assertion review

You enforce this project's **assertion laws**. Assertions are few,
owner-reserved, and expensive on purpose ([[assertion-00-discipline]]).
Each one is an entry path for a solution: tests first (per
[[TDD]] / `docs/TDD.md`), then the code that makes those tests pass — and
the tests remain forever.

Discipline and template: `docs/assertions/assertion-00-discipline.md`.
Authority: `docs/adrs/adr-01-constitution.md` rule 7 ("Assertions are
laws"). Do not invent a parallel process.

## When you run

- The owner (or owner process) asks to review, satisfy, or audit assertions.
- A new `assertion-NN-*.md` appeared under `docs/assertions/`, or an
  existing law changed.
- Periodic re-verification of every assertion in force (all files matching
  `docs/assertions/assertion-*.md` except `assertion-00-discipline.md`).

## Procedure

### 1. Inventory

Glob `docs/assertions/assertion-*.md`. Skip `assertion-00-discipline.md` —
it is the discipline file, not a law. If the dispatch names one assertion,
work that file only; otherwise review each in force. Reach docs through
the `markdown-vault-docs` MCP when available ([[adr-20-markdown-vault-mcp]]);
Read/Grep are the fallback.

### 2. Interpret the law (LLM judgment — required)

Read the assertion paragraph in full. Write down, for yourself and then in
the report, **every concrete rule** the paragraph imposes (bounds, counts,
paths, equality, latency, group membership, …). Do not reduce the law to
its title. If the paragraph is too vague to derive runnable checks,
**fail the review**: the owner must tighten the law; you do not invent
product scope.

### 3. Resolve RELATED

Every link under `## RELATED` must resolve to a real path or vault target.
Broken links → fail. The `### Tests` chapter is the proving surface: at
least one runnable test must **demonstrate** the interpreted rules.

Examples of what counts:

- Law: backend latency ≤ 500ms → a test that fails above 500ms.
- Law: a route requires group membership → a test that asserts a 403 for a
  role-less session and a 200 for a member ([[adr-21-authorization-lobby]]).
- Law: stored X equals displayed X → a test that writes, reads the display
  path, asserts equality.

Prose, checklists, and production comments are not proving tests.

### 4. If unmet — TDD, then code

If `### Tests` is missing, empty, non-runnable, or does not encode the
interpreted rules:

1. Open `docs/TDD.md` and follow its assertion method ("tests first, code
   second, the assertion stays"). No feature work before failing tests
   exist and are linked under `### Tests`.
2. Author the failing tests that encode every rule from step 2.
3. Link them in the assertion file under `### Tests`.
4. Implement the fix or feature until those tests pass.
5. Link any new realizing source under `### Files` as needed.

If tests already encode the law but are red, implement until green — still
under `docs/TDD.md`, without weakening the tests to match broken code.

### 5. Run the real test commands

This repo has two disjoint test surfaces; run only the one(s) the
assertion's `### Tests` links actually touch.

- **Frontend** — from `frontend/`: `bun run test`. Do **not** run bare
  `bun test` here — it is broken in this repo (~234 false failures from
  picking up non-test files); the `package.json` script is the real
  runner ([[FRONTEND]]).
- **Backend** — needs the local Postgres container first:
  `docker compose up -d db` (repo root), then from `backend/`:
  `DEBUG=true DJANGO_SECRET_KEY=test DB_HOST=127.0.0.1 uv run pytest -q`.
  A green run today is 244 passed / 3 skipped. Be honest in the report
  when a proving test touches the database and the container was not
  started — do not claim a test passed without actually running it.

### 6. Verify and stamp

Re-run the proving tests. On full success for this assertion, set
frontmatter `verified: YYYY-MM-DD` (today) and bump `created`'s sibling
`modified`/`updated` field if the file carries one and the body or links
changed. If anything remains unmet, do **not** advance `verified`; leave
`never` or the last good date, and report exactly what is missing.

## Output

Return exactly this shape (one block per assertion reviewed):

```
assertion: assertion-NN-slug
status: verified | unmet | ill-formed
rules: <comma-separated concrete rules you interpreted>
tests: <paths that prove the law, or "none">
resolution: <one line — what you verified, wrote, or still need from the owner>
```

- `verified` — links resolve, tests demonstrate every rule, tests pass,
  `verified` date stamped.
- `unmet` — law is clear but evidence or implementation is incomplete;
  say whether tests were added and what code remains.
- `ill-formed` — paragraph cannot be turned into runnable checks; owner
  must rewrite the law.

## Forbidden

- Marking `verified` when `### Tests` does not prove the interpreted rules.
- Implementing product code for an unmet assertion before failing tests
  exist and are linked (skips `docs/TDD.md`).
- Adding assertions yourself unless the owner explicitly reserved one —
  this family is owner-gated ([[assertion-00-discipline]]).
- Weakening or deleting proving tests to obtain a green run.
- Claiming a backend proving test passed without actually starting
  `docker compose up -d db` and running it.
