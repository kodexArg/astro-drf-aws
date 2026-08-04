---
title: adr-01-constitution
type: adr
category: harness
use_case: writing or amending the PRD or a constitution doc, deciding whether a document belongs in the constitution tier or loose docs/, settling authority between the PRD, the ADRs, and other markdown
created: 2026-08-04
modified: 2026-08-04
tags: [adr, harness, constitution, prd, assertions]
---

# ADR-01 — constitution (source markdown)

## CONTEXT

> This is the first and main ADR of the project law. It binds the source
> markdown: PRD, constitution, living docs, and the ADR family — what counts
> as written truth and in what order.

Rules only. How the pieces fit in prose lives in [[HARNESS]]; document shape
lives in [[CONVENTION]] and this family's `adr-00`.

## ASSERTIONS

1. **Authority order.** [[PRD]] is the objective at the top. Beneath it sits
   the rest of `docs/constitution/` — how the project is run. Beneath that
   sit the ADRs in `docs/adrs/` — the binding decisions. Beneath those sit
   every other document under `docs/`. Where layers disagree, the higher
   layer wins; where an ADR and the code disagree, the ADR wins
   ([[adr-00-adr-doctrine]] rule 10).
2. **[[PRD]] is mandatory and short.** It states what the product is, who it
   serves, and the horizon. Behavior, stories, requirements, and any project
   law are not inlined there — they live with their owners and are reached
   by wikilink from the PRD.
3. **Constitution tier.** A file earns `docs/constitution/` only when it is
   both meaningful and stable. Changing the constitution is an event.
   Meaningful-but-volatile or stable-but-unimportant material lives directly
   under `docs/`.
4. **ADRs are load-bearing.** Presence in `docs/adrs/` is what makes a
   decision binding ([[adr-00-adr-doctrine]] rule 6). Complying with every
   ADR in force is a precondition for adding anything to the project (rule
   9). This ADR is the entry point for the project's written law beneath
   [[PRD]]; every other ADR specializes a theme beneath it.
5. **Families accumulate; the constitution tier sorts.** `docs/adrs/` and
   `docs/assertions/` are numbered families, each ruled by its own `-00`
   discipline file (`adr-00-adr-doctrine`, [[assertion-00-discipline]]).
   Neither sorts by stability — both append. Sorting by "meaningful and
   stable" applies only to constitution vs. loose `docs/` documents.
6. **The ABC gate is this order, applied.** Every request checks, in order:
   does it follow [[PRD]]; does it comply with the ADRs in force; does it
   modify [[API]] ([[AGENTS]]). This ADR is why that order is checked in
   that sequence — rule 1's authority order, applied to a single change.
7. **Assertions are laws.** Owner-reserved, kept few, optional as a set —
   a project with zero assertions is healthy. Every assertion that exists
   under `docs/assertions/` must be met via proving tests linked from its
   own body ([[TDD]], [[assertion-00-discipline]]). They are an entry path
   for important features, beneath the ADRs in the authority order of rule
   1. When an assertion and the constitution disagree, the assertion is
   the one that is wrong ([[assertion-00-discipline]]).
8. **Knowledge under `docs/`.** Everything the project *knows* lives under
   `docs/`. `backend/` and `frontend/` hold what the project *is*. Facts
   that an ADR rule stands on live in `docs/` documents and are reached by
   wikilink — never inlined into the ADR ([[adr-00-adr-doctrine]] rule 1).

## FORBIDDEN

- **NEVER** put product behavior, use cases, or project law into the PRD
  body (rule 2). That duplicates owners and drifts.
- **NEVER** treat a document outside `docs/adrs/` as an ADR, or an ADR
  outside that directory as binding (rule 4).

## RELATED

### governed paths

- `docs/constitution/` — stable binding tier, [[PRD]] included
- `docs/` — loose documents that iterate with the code
- `docs/adrs/` — decision family
- `docs/assertions/` — law family

### related files

- [[adr-00-adr-doctrine]] — ADR shape and lifecycle this ADR obeys
- [[adr-02-harness]] — how skills, hooks, and agents attach to this law
- [[HARNESS]] — tiers, vault, and the harness in prose
- [[PRD]] — the objective
- [[CONVENTION]] — global frontmatter
- [[API]] — the third gate of the ABC in rule 6
- [[AGENTS]] — the ABC gate itself
- [[assertion-00-discipline]] — the law family's own discipline
- [[TDD]] — the tests-first method assertions drive
