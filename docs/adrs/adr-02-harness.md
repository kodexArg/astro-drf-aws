---
title: adr-02-harness
type: adr
category: harness
use_case: adding or editing a skill hook or agent, vendoring a skill into the repo, deciding whether tooling may invent law, closing a batch that touched agent tooling
created: 2026-07-10
modified: 2026-08-04
tags: [adr, harness, skills, hooks, agents]
---

# ADR-02 — harness tooling (skills, hooks, agents)

## CONTEXT

> The harness is the agent surface that serves the written law. Skills,
> hooks, and agents live beside that law — they do not replace it, invent
> it, or keep a second copy of it.

Rules only. What each tool does in detail lives in [[HARNESS]]; guardian and
delivery themes have their own ADRs.

## ASSERTIONS

1. **Tooling homes.** Skills live under `.claude/skills/`, agent definitions
   under `agents/`, hooks under `.claude/hooks/`. These folders are part of
   the harness, excluded from the vault index, and reached by path — not as
   vault notes.
2. **Law first.** Every skill, hook, and agent **obeys** [[adr-01-constitution]]
   and every ADR in force. Tooling may interpret and enforce the law; it
   must not silently redefine the objective, invent constitution policy, or
   invent product law. When tooling and law disagree, the law is right and
   the tooling is the defect.
3. **Explicit links.** Agent and skill bodies that act on written law name
   the governing documents by wikilink or path: [[PRD]], constitution files,
   the ADR set, [[TDD]] as relevant. A tool that gates a surface without
   pointing at its governing ADR or doc is incomplete.
4. **One real copy of a skill, vendored.** The required skill set is exactly
   what [[HARNESS]] lists. A skill absent from that table is not part of the
   template's harness; adding one to the repo means adding its row first, in
   the same batch. Every required skill is vendored as a real copy,
   self-contained, under `.claude/skills/<name>/` — the home the harness
   loads — mirrored under `skills/<name>/`; the two stay in sync. The
   template never depends on the machine-global symlink harness
   (`~/.agents/skills/`, `~/.claude/skills/`): a fresh clone exposes the full
   set with no external links.
5. **Agents are part of the harness but are not skills.** SSOT for agent
   definitions is `agents/`, reached as `.claude/agents/` and
   `.agents/agents/` through links — one real copy, links everywhere else
   ([[adr-03-guardians]] rule 2 for guardians). Adding an agent still
   requires its [[GLOSSARY]] row.
6. **Skills are playbooks.** A skill is an instruction package under
   `.claude/skills/<name>/SKILL.md` (plus its local references, bin, tests),
   wired into the runtime's skill discovery. The stack and DevOps skills are
   the sanctioned path for their domains, not optional aids: frontend
   through `kdx-astro-7`, backend through `kdx-django-6-drf`, AWS through
   the `kdx-aws-*` set; vault `.md` is written through `obsidian-markdown`;
   go/no-go triage through `kdx-triage`; multi-step fan-out through
   `kdx-orchestrator`.
7. **Hooks are automation.** Hooks are scripts attached to agent or git
   lifecycle events. The dispatch safety net (`.claude/hooks/dispatch_guardians.py`)
   belongs here; its binding duty is [[adr-03-guardians]].
8. **Skills carry no information ADRs would otherwise own.** Where a skill
   and a doc disagree on a rule, the ADR-backed doc wins; a skill is a
   procedure, the SSOT doc is the truth.

## FORBIDDEN

- **NEVER** keep a second SSOT for a skill outside `.claude/skills/<name>/`
  (rule 4). The `skills/` mirror stays in sync, never diverges.
- **NEVER** keep a second SSOT for agent definitions outside `agents/`
  (rule 5).
- **NEVER** let a skill or agent stamp or invent product law without the
  owner (rule 2). Decisions belong in `docs/adrs/`.
- **NEVER** put durable project decisions only inside a skill prompt with no
  ADR (rule 2).

## RELATED

### governed paths

- `.claude/skills/` and `skills/` — vendored skill packages, kept in sync
- `.claude/hooks/` — lifecycle automation
- `agents/` — agent definitions (guardians + orch-*/wf-* cast), linked from
  `.claude/agents/` and `.agents/agents/`

### related files

- [[adr-01-constitution]] — the written law this tooling serves
- [[adr-03-guardians]] — guardian agents and dispatch safety net
- [[adr-04-issue-delivery]] — issue → worktree → PR mechanics
- [[HARNESS]] — tooling section in prose
