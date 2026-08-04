---
title: adr-00-adr-doctrine
type: adr
category: harness
use_case: writing, editing, or reviewing any ADR; deciding how a rule is cited, retired, or recorded
created: 2026-07-10
modified: 2026-08-04
tags: [adr, discipline]
---

# ADR-00 — the ADR discipline

## CONTEXT

> Every ADR here has one shape and one theme, and outlives its own policies.
> This is that shape, and what happens when a decision changes.

An ADR states rules, never information. Facts, tables, specs and explanations
live in `docs/` and are reached by wikilink; if an ADR needs a fact, it links
the doc that owns it — it never inlines it.

## ASSERTIONS

1. An ADR states rules. Every fact, table, spec, or explanation a rule stands
   on lives in a `docs/` document and is reached by wikilink.
2. An ADR lives in `docs/adrs/`, named `adr-NN-slug.md` — sequential
   two-digit `NN`, kebab-case English slug ([[GLOSSARY]], [[LOCALISATION]]).
   `adr-00` is reserved for this discipline.
3. Frontmatter carries exactly these seven fields, in this order: `title`
   (the filename without `.md`), `type` (always `adr`), `category` (one of
   `frontend`, `backend`, `devops`, `harness`, `project`), `use_case` (the
   trigger — the act that should send a reader to this file — comma-separated
   on one inline line, never a topic restatement), `created` (`YYYY-MM-DD`,
   never changes again), `modified` (`YYYY-MM-DD`, updated on every edit),
   `tags` (lowercase, `adr` first).
4. An ADR has five level-2 sections, in this order: `CONTEXT` (a short quoted
   paragraph, optionally up to two plain paragraphs, no links), `ASSERTIONS`
   (the numbered rules), `FORBIDDEN` (optional — present only when the ADR
   forbids something outright; each entry opens with **NEVER**, states the
   prohibited act, names the rule it enforces, and gives why), `REJECTED`
   (the alternatives weighed and not taken, and every policy this ADR once
   held and holds no longer — each entry gives the reason it lost and, where
   one exists, the condition that would reopen it), `RELATED` (every link the
   ADR carries, grouped under level-3 headings). `FORBIDDEN` and `REJECTED`
   are omitted while empty.
5. A rule is cited from anywhere as `adr-NN` rule `M`, so its number is
   permanent: a rule is appended, never renumbered.
6. Presence in `docs/adrs/` is what makes a rule binding. Complying with every
   ADR in force is a precondition for adding anything to this project.
7. An ADR is attached to a theme and lives as long as that theme does. Its
   policy may change many times without the file ever moving or being
   renumbered: the theme is what the ADR is, the policy is only what it
   currently says.
8. Changing a policy is done in place, and the policy being replaced moves
   into `REJECTED` in the same edit — so the body always reads as one current
   truth while the ADR keeps the record of what it used to require. A policy
   change is a decision and is made only with the owner's authorization,
   given in the conversation where it happens. A cosmetic edit — a typo, a
   format, a repaired wikilink, a clearer sentence — changes nothing else and
   needs no authorization. Every edit sets `modified` to that day.
9. `docs/` content is reached through the vault (`markdown-vault-docs` MCP)
   before Grep or Read for anything that is `docs/` prose or its wikilink
   structure ([[adr-20-markdown-vault-mcp]]). Grep/Read stay correct for
   code, configs, and non-`docs/` files.
10. An ADR is the source of truth for the decision it records, and it
    outranks the code implementing it: where the two disagree, the ADR is
    right and the code is the defect. Authority runs [[PRD]] first, then the
    rest of the constitution, then the ADRs, then every other document,
    [[API]] included.

## FORBIDDEN

- **NEVER** inline a fact in an ADR (rule 1). An ADR that carries its own
  facts becomes a second source of truth for them, and the two drift.
- **NEVER** state the same rule in two ADRs (rule 1). One ADR owns a rule;
  every other links to it.
- **NEVER** renumber a rule (rule 5). Citations elsewhere point at the
  number.
- **NEVER** drop a policy without recording it in `REJECTED` (rule 8). A
  rule that simply vanishes leaves the code that obeyed it looking wrong for
  a reason nobody can find again. Doubt about whether an edit changes policy
  resolves to recording it.
- **NEVER** leave a superseded policy standing beside the rule that replaced
  it (rule 8). The body is current truth; the history lives in `REJECTED`.

## REJECTED

- **A `status: active | defered` frontmatter field on every ADR** — the shape
  this discipline held until 2026-08-04. Dropped because the directory
  already answers the question (rule 6): a file present in `docs/adrs/` is
  binding, a second answer alongside it can only disagree with the first. It
  would reopen only if an ADR ever needed to sit in `docs/adrs/` without
  binding, which is not a known need.
- **An immutable body with supersession chains** — the policy this
  discipline held until 2026-08-04: once written, an ADR's body froze, and
  every change of mind spawned a new ADR number that superseded the old one,
  which was then hollowed to bare frontmatter under `docs/obsolete/`. It kept
  each file's text immutable, but it scattered one theme across a chain of
  numbers, so the current answer could only be found by walking the chain,
  and the ADR count grew with the project's mind changing rather than with
  its concerns. Replaced by rule 7 — the theme holds the number, the policy
  moves through `REJECTED` in place. It would reopen only if an ADR's
  history grew long enough to bury its current rules, which is a reason to
  split the theme, not to retire the file.
- **`docs/obsolete/defered-adr-NN-slug.md` hollow stubs** — the retired file
  staying in place with its frontmatter and an empty body, once its theme
  fully superseded. Dropped together with the supersession chain above:
  under rule 6 a file present in `docs/adrs/` reads as in force, and a
  hollow one would read as a rule with no content. `docs/obsolete/` held no
  populated files at the time of this change (2026-08-04) and is removed.
- **This project's former 00–24 sequential numbering under the supersession
  model above** — retired 2026-08-04 in the same batch as this rewrite,
  owner-ruled: `adr-00` through `adr-04` are re-themed to the five
  harness-default doctrine files (this discipline, the constitution, harness
  tooling, guardians, issue delivery), absorbing this project's former
  `adr-11-guardians` and `adr-14-harness` as named additions; the twenty
  surviving product ADRs are renumbered `05`–`25` with every rule's text and
  number preserved inside the moved file. This is a one-time exception to
  rule 7 (a theme holds its number for life), authorized in this
  conversation; it authorizes nothing beyond this migration.

## RELATED

### governed paths

- `docs/adrs/` — every ADR, all in force

### related files

- [[AGENTS]] — the ABC gate this discipline is a precondition for
- [[GLOSSARY]] — naming authority for every ADR term
- [[PRD]] — the top of the authority order in rule 10
- [[API]] — the contract every route answers to, ADR-outranked per rule 10
- [[adr-20-markdown-vault-mcp]] — the vault-first read path of rule 9
