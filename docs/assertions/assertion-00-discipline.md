---
title: assertion-00-discipline
type: reference
status: active
created: 2026-08-04
tags: [harness, assertions, tdd]
---

# Assertion-00 — assertion discipline

## What an assertion is

An assertion is a **law** the project must pass — never a wish, never a
backlog item. It is a Gherkin use case collapsed into one paragraph,
written concretely enough that an agent can interpret every rule it
imposes and demand the tests that prove them.

> The user can get their last three messages, three clicks away from the
> home page, in a query, in less than 2 seconds.

That paragraph states the rules: what (the last three messages), how far
(three clicks from home), how (one query), how fast (under 2 seconds). An
assertion that cannot be checked is not an assertion.

**Assertions are the entry path for solutions.** The owner writes the law;
whoever reviews it interprets it, demands the proving tests via [[TDD]],
and that work prepares the fix or feature — above all the tests that
always verify the law. Tests first, code second; assertion, tests, and
code coexist in the project.

## Why they are few

Each assertion costs real compute: interpretation, test authoring,
implementation, and periodic re-verification. They are **reserved for the
owner**. A project with zero assertions is healthy. Presence is what
binds — every assertion that exists must be met.

## Naming

```
assertion-NN-descriptive-slug.md
```

- `NN` is a two-digit, zero-padded number: `01`, `02`, …
- The slug is lowercase, hyphenated, no accents or special characters.
- `assertion-00` is reserved for this discipline file.

## Frontmatter

Assertions extend the base convention ([[CONVENTION]]) with one extra key:

```yaml
title: assertion-NN-slug
type: reference
status: active
created: YYYY-MM-DD
verified: YYYY-MM-DD | never
tags: [assertion]
```

`verified` is the date of the last successful review — the date an agent
actually ran every linked test and watched it pass. `never` means the law
has not yet been reviewed, or its proof no longer holds.

## Format

The assertion paragraph comes first and states the rules. The file ends
with a `## RELATED` section: an open/close list, organized in `###`
chapters, linking everything that realizes or verifies the assertion —
**tests first**, then source files, docs. Entries open and close as the
project evolves; the list is expected to churn even though the assertion
itself stays put.

### Tests chapter is mandatory

At least one link under `### Tests` must point at a runnable test that
**demonstrates** the law. A promise with no proving test is not an
assertion — it is a wish. Until that link exists and the test encodes
every rule the paragraph states, the assertion is unmet: work follows
[[TDD]] — demand the failing tests, link them, implement until green —
rather than being marked verified.

## Review

A review of an assertion:

1. Reads the assertion (or the one named in the dispatch).
2. Interprets with judgment what the paragraph requires — every concrete
   rule, never a paraphrase of the title.
3. Resolves every `## RELATED` link; a broken link fails the review.
4. Confirms `### Tests` proves the law by actually running the linked
   tests. If they do not exist, do not pass, or do not cover every rule,
   the reviewer stops adding features and executes [[TDD]] instead.
5. On success, sets `verified` to the date the tests were actually run and
   seen green. On failure, leaves `verified` as `never` (or the last good
   date) and reports what is missing.

## Alignment

Assertions are always aligned with [[PRD]] and the rest of
`docs/constitution/`. They are the constitution made verifiable: if an
assertion drifts from what the constitution says, the assertion is the one
that is wrong.

## Template

Copy this block as the starting point for a new assertion.

```markdown
---
title: assertion-NN-slug
type: reference
status: active
created: YYYY-MM-DD
verified: never
tags: [assertion]
---

[The assertion: one paragraph stating what must be accomplished, with
every rule it imposes — concrete enough to be checked.]

## RELATED

### Tests

- [link to a runnable test that demonstrates this law]

### Files

- [link]

### Docs

- [link]
```
