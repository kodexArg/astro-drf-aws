---
title: CODE-COMMENTS
type: reference
status: active
created: 2026-08-04
tags: [doc, ssot, code-style, comments]
---

# CODE-COMMENTS — how much a comment may say

SSOT for comment length and content across this repository's code. Given
force by [[adr-26-comment-brevity]]. Language is English, always
([[LOCALISATION]], [[adr-05-glossary-and-localisation]] rule 3) — this file
governs *how much*, never *which language*.

> [!warning] The failure this exists to stop
> Multi-paragraph comments that narrate rationale, restate ADRs, argue with
> alternatives, or justify a decision to a reader. They out-grow the code,
> drift from it silently, and become a second, unversioned SSOT — the same
> disease [[adr-00-adr-doctrine]] rule 1 forbids in an ADR and
> [[adr-19-live-doc-backlinks]] rule 2 forbids in a live-doc block.

## The limits

| Kind | Limit | May say |
|---|---|---|
| Live-doc block | as the linker writes it | wikilinks only, never prose ([[adr-19-live-doc-backlinks]] rule 2) |
| File header | **≤ 3 lines** | what the file is, in one breath; a wikilink for the rest |
| Inline / block | **≤ 2 lines** | the non-obvious *why* of the line below it |
| Docstring / JSDoc on a symbol | **≤ 2 lines** per symbol | what the parameter or return *is* |

A comment over its limit is a defect, fixed by deleting it or by moving what
it says into the doc that owns the subject. This applies to every language
this project's stack carries — `.py` ([[BACKEND]]), `.astro`/`.svelte`/`.ts`
([[FRONTEND]]), `.yaml`, tests included ([[adr-26-comment-brevity]] rule 4).

## What a comment must never do

1. **Restate the code.** If the line reads
   `if not request.user.is_authenticated: return HttpResponseForbidden()`, it
   needs no comment.
2. **Restate a rule.** Cite `[[adr-NN-slug]]` or the doc; never paraphrase
   what it requires. The doc wins, so a paraphrase can only ever be a stale
   second copy.
3. **Argue.** No "chosen because", no rejected-alternative survey, no
   "deliberately", no defense of the design against an imagined reviewer.
   That belongs in the PR, the issue, a [[BDD]]/[[TDD]] entry, or an ADR's
   `CONTEXT`/`REJECTED`.
4. **Narrate history.** No "used to be X", no "changed in #NNN". Git owns
   that.
5. **Teach.** No explanation of how a framework, browser, or language
   feature works.

## Where the prose goes instead

Rationale is not lost, it is *relocated* — to the surface that is reviewed
and versioned as prose:

- a design decision → the ADR that rules it, or the doc that ADR points at
- a feature's behavior → its [[BDD]] entry
- a backend unit's contract → its [[TDD]] entry
- the reason for one commit's shape → the commit message or the PR body
  ([[GH]])

## The one-line test

Read the comment. If deleting it would lose nothing a reader of the code
plus its linked docs could recover, delete it. Most comments fail this test.
