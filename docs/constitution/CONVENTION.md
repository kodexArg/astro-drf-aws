---
title: CONVENTION
type: reference
status: active
created: 2026-08-04
tags: [harness, convention, frontmatter]
---

# CONVENTION — frontmatter for ADRs and docs/*

Global convention for every markdown document under `docs/` (constitution,
loose docs, ADRs, BDDs, TDDs). Adopted from harness-default
([[HARNESS]]) as the binding vault-wide standard; this file is itself
`docs/constitution/` because it is both meaningful and stable.

## Frontmatter documentation

Every markdown document under `docs/` opens with a YAML frontmatter block —
`---` on line 1. It is the machine-readable summary of the document: agents
read it to decide whether the file is worth opening, and tooling indexes it
without parsing prose.

Tooling files are exempt: `.claude/skills/`, `skills/`, `agents/`, and
`.claude/hooks/` obey the formats their tools fix (a skill's `SKILL.md`
carries `name` + `description`), not this convention.

Required keys for this template's constitution/loose/BDD/TDD docs:

| Key | Value |
|---|---|
| `title` | Short human-readable title, matching the filename's canonical form ([[GLOSSARY]]). |
| `type` | One of `prd`, `reference`, `bdd`, `tdd` — the document's family (`adr` is out of scope here; see below). |
| `status` | `active` or `defered`. Presence with `status: active` is what makes the document current. |
| `created` | Date the document was first written, `YYYY-MM-DD`. |
| `tags` | Flat list of lowercase topic tags. |

An ADR carries its own, different frontmatter shape and needs no `status`
field: presence in `docs/adrs/` is what makes it binding
([[adr-00-adr-doctrine]] rules 2–3, 6).

Rules:

- Frontmatter is the first thing in the file: `---` on line 1.
- Keys are lowercase and flat (no nesting); values are plain YAML scalars or
  a flat list.
- A document that is present and `status: active` is valid — validity lives
  in the tree, not in prose commentary.
- An ADR is never superseded or hollowed: a policy change is made in place,
  with the replaced policy recorded in that ADR's `REJECTED` section
  ([[adr-00-adr-doctrine]] rule 8). `docs/obsolete/` is retired along with
  the supersession-chain model it served ([[adr-00-adr-doctrine]] REJECTED).
- Document families may extend the base set with their own keys — ADRs
  additionally always link `[[wikilinks]]`, never inline facts
  ([[adr-00-adr-doctrine]] rule 1).

## Where a document sorts

Two tiers hold written knowledge outside the ADR/BDD/TDD families:

- **`docs/constitution/`** — meaningful *and* stable: read first, settles
  arguments, amended rarely and deliberately. Current residents: [[PRD]],
  [[REQUIREMENTS]], [[HARNESS]], [[INFRASTRUCTURE]], [[LOCALISATION]], and
  this file.
- **`docs/` (loose)** — everything else: documents that iterate with the
  code ([[API]], [[BACKEND]], [[FRONTEND]]) or are stable reference but not
  load-bearing ([[GLOSSARY]], [[VARIABLES]], [[GH]]).

Test for a new document: would changing it alter how the project is run,
*and* do we expect it to stay unchanged? Only a yes to both puts it in
`docs/constitution/`.
