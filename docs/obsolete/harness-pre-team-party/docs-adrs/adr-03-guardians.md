---
title: adr-03-guardians
type: adr
category: harness
use_case: closing a batch of changes that touched PRD, an ADR, or API.md, defining or dispatching a guardian, editing a guardian's watch list or the dispatch safety net, acting on a guardian verdict, running dispatch from outside Claude (another agent, CI, or a human at the CLI)
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
8. **A guardian's watchlist has one machine copy: the `watch:` glob list in
   the frontmatter of its own definition, beside the prose that explains
   it.** The dispatch safety net — `docs/hooks/guardian-dispatch`, the
   runtime-agnostic script any harness or a human can call, plus its
   Claude-native PostToolUse wrapper `.claude/hooks/dispatch_guardians.py`,
   which delegates to it rather than carrying a duplicate — reads only that
   key; a watched surface enters or leaves the watchlist by editing the
   guardian's file, nowhere else. One machine copy cannot drift from itself.
9. **Fast dispatch via `--bundle`.** The owner process (or `docs/hooks/pre-commit`,
    name-only, at commit time) runs `docs/hooks/guardian-dispatch --bundle
    [<ref>|--staged]` to produce the dispatch payload: the owed guardians and
    their hit files, a unified diff scoped to those hit files, and a live ADR
    `use_case` index built from each ADR's own frontmatter. The owner pastes
    that payload into each owed guardian's prompt and dispatches all of them
    in one turn (rule 3) — the guardian does not rediscover the batch alone;
    it uses the payload as its working surface, and the index lets its
    triage step (rule 7) resolve most dispatches without opening an ADR
    body.

## REJECTED

- **Two-place watchlist** — the policy this project held before this
  rewrite (2026-08-04, owner ruling): each guardian's Watchlist section
  in prose PLUS a hand-kept `WATCHLISTS` dict in the dispatch hook, required
  to stay identical in coverage by a since-retired rule. Replaced by rule 8.
  It lost because a two-place list can only ever drift from itself — a
  single machine-read source (the guardian's own frontmatter) removes the
  possibility structurally instead of policing it by convention. It would
  reopen only if a runtime existed that could not read a guardian's own
  frontmatter, which none in scope cannot.
- **Guardian rediscovers the batch alone** — the policy held before the
  2026-08-04 rewrite: an owed guardian Globs/greps the change set itself
  with no payload handed to it. Replaced by rule 9. It would reopen only
  if the owner process could not assemble the payload before dispatch.

## RELATED

### governed paths

- `agents/astro-drf-aws-prd.md`, `agents/astro-drf-aws-adr.md`,
  `agents/astro-drf-aws-api.md` — this project's three guardians, each
  carrying its own `watch:` frontmatter list (rule 8)
- `docs/hooks/guardian-dispatch` — the runtime-agnostic dispatch script
  (rules 3, 8, 9); `docs/hooks/pre-commit` speaks it at commit time
  (name-only, manual `ln -s` install, never installed automatically)
- `.claude/hooks/dispatch_guardians.py` — the Claude-native PostToolUse
  safety net (rule 3); delegates to `docs/hooks/guardian-dispatch` for the
  watchlist (rule 8) and carries no duplicate of its own

### related files

- [[adr-00-adr-doctrine]] — the discipline both guardians enforce and obey
- [[adr-01-constitution]] — written law the guardians protect
- [[adr-02-harness]] — tooling home for agents and hooks
- [[PRD]] — the document the PRD guardian owns
- [[API]] — the document the API guardian owns
- [[GLOSSARY]] — the term "guardian" and the naming gate for adding one
