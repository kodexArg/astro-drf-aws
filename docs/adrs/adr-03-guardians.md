---
title: adr-03-guardians
type: adr
category: harness
use_case: closing a batch of changes that touched PRD, an ADR, or API.md, defining or dispatching a guardian, editing a guardian's watch list or the dispatch safety net, acting on a guardian verdict
created: 2026-07-10
modified: 2026-08-04
tags: [adr, harness, guardians, agents]
---

# ADR-03 — guardian agents

## CONTEXT

> Three guardians watch the health of this project's law: `astro-drf-aws-prd`
> guards the objective, `astro-drf-aws-adr` guards the rules, and
> `astro-drf-aws-api` guards the contract. This ADR is what makes their
> verdicts binding.

Rules only; what each guardian is — posture, watchlist, output shape — lives
in its definition under `agents/`.

## ASSERTIONS

1. **This project runs three guardians**: `astro-drf-aws-prd`,
   `astro-drf-aws-adr`, and `astro-drf-aws-api` — the verification gate for
   [[PRD]], the set of ADRs in force, and [[API]] respectively. One guardian
   per in-memory concern; adding a guardian requires its [[GLOSSARY]] row
   and an appended rule here.
2. SSOT for guardian definitions is `agents/`; `.claude/agents/` and
   `.agents/agents/` are links to it. One real copy, links everywhere else.
3. Guardians are sought, not only triggered. An owner process that intends
   to modify a guardian's SSOT or watched surface engages that guardian for
   the change; the `dispatch_guardians.py` nudge is the safety net for the
   case it forgot, and is equally binding — one dispatch per guardian per
   batch, before the batch closes, honoring the returned `notify` list.
4. Guardians report; they never dispatch. Sibling notification flows only
   through the owner process. A guardian ignores dispatch nudges that name
   itself.
5. A guardian verdict of `violation` / `defect` / `danger` blocks the change
   until resolved; `needs-new-adr` routes through the ADR lifecycle
   ([[adr-00-adr-doctrine]]), never through a local exception.
6. A guardian's output shape (`status` / `resolution` / `notify`) is fixed
   by its definition file. Guardians run on sonnet.
7. Guardians triage before they sweep. A dispatch that touches nothing in
   the guardian's domain returns its passing verdict in one line,
   immediately — false positives are dismissed fast; depth is spent only on
   plausible concerns.
8. Watchlists exist in exactly two places — each guardian's Watchlist
   section and the hook's `WATCHLISTS` — and must stay identical in
   coverage; a divergence is a defect fixed in the same batch that finds it.
9. **Fast dispatch payload.** The owner process assembles, for each owed
   guardian, the hit files, a diff scoped to those hit files, and a live ADR
   `use_case`/topic index, and pastes that payload into the guardian's
   prompt rather than leaving it to rediscover the batch alone. When more
   than one guardian is owed, the owner dispatches them in parallel in one
   turn.

## REJECTED

- **Guardian rediscovers the batch alone** — the policy this project held
  before this rewrite (2026-08-04): an owed guardian Globs/greps the change
  set itself with no payload handed to it. Replaced by rule 9. It would
  reopen only if the owner process could not assemble the payload before
  dispatch.

## RELATED

### governed paths

- `agents/astro-drf-aws-prd.md`, `agents/astro-drf-aws-adr.md`,
  `agents/astro-drf-aws-api.md` — this project's three guardians
- `.claude/hooks/dispatch_guardians.py` — the dispatch safety net (rules 3, 8, 9)

### related files

- [[adr-00-adr-doctrine]] — the discipline both guardians enforce and obey
- [[adr-01-constitution]] — written law the guardians protect
- [[adr-02-harness]] — tooling home for agents and hooks
- [[PRD]] — the document the PRD guardian owns
- [[API]] — the document the API guardian owns
- [[GLOSSARY]] — the term "guardian" and the naming gate for adding one
