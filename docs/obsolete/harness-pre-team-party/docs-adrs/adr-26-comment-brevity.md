---
title: adr-26-comment-brevity
type: adr
category: harness
use_case: writing or reviewing a code comment, deciding whether a rationale belongs in code or in a doc, writing a docstring
created: 2026-08-04
modified: 2026-08-04
tags: [adr, code-style, comments, doctrine]
---

# ADR-26 — comment brevity

## CONTEXT

> A comment states the non-obvious why and nothing else. Everything longer
> — a rule, a decision, a history — relocates to the doc that owns it.

Rules only; the per-kind line limits and the five prohibitions live in
[[CODE-COMMENTS]]. This ADR adds a code-style requirement across the whole
repository (owner directive, in conversation, 2026-08-04); near-zero
comments is the deliberate target.

## ASSERTIONS

1. A comment in code is brief. The per-kind line limits are owned by
   [[CODE-COMMENTS]] and are binding: a comment exceeding its limit is a
   defect, corrected by deleting it or relocating what it says — never by
   rewording it shorter while keeping the essay's job.
2. A comment states the non-obvious *why* and nothing else. It MUST NOT
   restate the code, restate a rule, argue a decision, narrate history, or
   teach a language or framework feature ([[CODE-COMMENTS]] — the five
   prohibitions).
3. Rationale is relocated, never deleted from the project. A design
   decision enters an ADR and the doc that ADR points at; a feature's
   behavior enters its [[BDD]] entry; a backend unit's contract enters its
   [[TDD]] entry; the reason for one change's shape enters the commit
   message or PR body ([[GH]]). A comment reaches those by wikilink and
   carries none of their content.
4. This applies to every language in the repository — `.astro`, `.svelte`,
   `.ts`, `.py`, `.yaml`, tests included. No file type and no directory is
   exempt.
5. The live-doc block is not a comment for this ADR's purposes; it is
   generated, and its wikilinks-only rule is already
   [[adr-19-live-doc-backlinks]] rule 2, unchanged here.

## FORBIDDEN

- **NEVER** let a comment exceed its per-kind line limit (rule 1). Trim by
  deletion or relocation, never by compressing the same content into fewer,
  denser lines.
- **NEVER** restate code, a rule, a decision, or history in a comment (rule
  2). Point at the doc that owns it instead.

## RELATED

### related files

- [[adr-19-live-doc-backlinks]] — the live-doc block's own wikilinks-only
  rule, which this ADR does not alter
- [[CODE-COMMENTS]] — per-kind limits, the five prohibitions, relocation
  targets
- [[BDD]] — where feature rationale relocates
- [[TDD]] — where backend-unit rationale relocates
- [[GH]] — commit message / PR body as a rationale target
