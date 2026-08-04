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

1. **Tooling homes, `docs/`-first.** Skills live under `docs/skills/`, agent
   definitions under `docs/agents/`, and Claude-event-bound hooks stay under
   `.claude/hooks/` (rule 7 — they are not host-agnostic executables and have
   no `docs/hooks/` counterpart to move to). `docs/skills/` and
   `docs/agents/` are the real, single copy of that tooling — documented
   beside the project's prose, visible to any agent reading `docs/`, not only
   a Claude-specific one. They are excluded from the vault index (rule 4) and
   reached by path — not as vault notes.
2. **Host paths are links, not copies.** Every host-specific path a runtime
   expects still resolves, but only as a symlink onto the `docs/` home:
   `.claude/skills/` → `docs/skills/`, root `skills/` → `docs/skills/`,
   `.claude/agents/` → `docs/agents/`, `.agents/agents/` → `docs/agents/`.
   The template still never depends on the machine-global symlink harness
   (`~/.agents/skills/`, `~/.claude/skills/`): a fresh clone exposes the full
   set with no external links — the self-contained guarantee moves from "one
   real copy under `.claude/`, mirrored" to "one real copy under `docs/`,
   linked from every host path a runtime needs it at."
3. **Law first.** Every skill, hook, and agent **obeys** [[adr-01-constitution]]
   and every ADR in force. Tooling may interpret and enforce the law; it
   must not silently redefine the objective, invent constitution policy, or
   invent product law. When tooling and law disagree, the law is right and
   the tooling is the defect.
4. **Explicit links.** Agent and skill bodies that act on written law name
   the governing documents by wikilink or path: [[PRD]], constitution files,
   the ADR set, [[TDD]] as relevant. A tool that gates a surface without
   pointing at its governing ADR or doc is incomplete.
5. **One real copy of a skill, vendored under `docs/`.** The required skill
   set is exactly what [[HARNESS]] lists. A skill absent from that table is
   not part of the template's harness; adding one to the repo means adding
   its row first, in the same batch. Every required skill is vendored as a
   real copy, self-contained, under `docs/skills/<name>/` — the SSOT home —
   reached through the `.claude/skills/` and root `skills/` links (rule 2).
6. **Agents are part of the harness but are not skills.** SSOT for agent
   definitions is `docs/agents/`, reached as `.claude/agents/` and
   `.agents/agents/` through links (rule 2) — one real copy, links everywhere
   else ([[adr-03-guardians]] rule 2 for guardians). Adding an agent still
   requires its [[GLOSSARY]] row.
7. **Hooks stay host-bound where the host binds them.** A hook wired to a
   Claude lifecycle event (`SessionStart`, `PreToolUse`, `PostToolUse`,
   `UserPromptSubmit` in `.claude/settings.json`) is Claude-specific tooling,
   not a host-agnostic executable, and stays under `.claude/hooks/` — it has
   no `docs/hooks/` counterpart because moving it there would not make it
   runnable by any other host. Only a genuinely host-agnostic executable
   (e.g. a plain git hook with no Claude event binding) is vendored under
   `docs/hooks/`; none of this project's nine hooks currently qualifies. The
   dispatch safety net (`.claude/hooks/dispatch_guardians.py`) is one of the
   nine; its binding duty is [[adr-03-guardians]].
8. **Skills are playbooks.** A skill is an instruction package under
   `docs/skills/<name>/SKILL.md` (plus its local references, bin, tests),
   wired into the runtime's skill discovery through the `.claude/skills/`
   link. The stack and DevOps skills are the sanctioned path for their
   domains, not optional aids: frontend through `kdx-astro-7`, backend
   through `kdx-django-6-drf`, AWS through the `kdx-aws-*` set; vault `.md`
   is written through `obsidian-markdown`; go/no-go triage through
   `kdx-triage`; multi-step fan-out through `kdx-orchestrator`.
9. **Skills carry no information ADRs would otherwise own.** Where a skill
   and a doc disagree on a rule, the ADR-backed doc wins; a skill is a
   procedure, the SSOT doc is the truth.

## FORBIDDEN

- **NEVER** keep a second SSOT for a skill outside `docs/skills/<name>/`
  (rule 5). `.claude/skills/` and root `skills/` are links, never a second
  copy that can diverge.
- **NEVER** keep a second SSOT for agent definitions outside `docs/agents/`
  (rule 6).
- **NEVER** let a skill or agent stamp or invent product law without the
  owner (rule 3). Decisions belong in `docs/adrs/`.
- **NEVER** put durable project decisions only inside a skill prompt with no
  ADR (rule 3).

## REJECTED

- **Vendored skills under `.claude/skills/`, mirrored by a second real copy
  under `skills/`** — this discipline's rule until 2026-08-04, owner-ruled
  in conversation that day to adopt the `kodexArg/harness-default` schema in
  full. Dropped because the mirror was two real, independently-writable
  paths for what was supposed to be one copy — the sync-discipline it
  demanded ("the two stay in sync") was a standing risk of drift, not a
  guarantee against it. The `docs/`-home + host-link design (rules 1–2)
  keeps exactly one real copy and makes every other path a link that cannot
  drift, while also making the tooling visible to any agent reading `docs/`
  prose, not only a Claude-specific one. It would reopen only if a runtime
  ever needed a genuinely independent, unlinked copy of a skill package,
  which is not a known need.

## RELATED

### governed paths

- `docs/skills/` — the SSOT of vendored skill packages; `.claude/skills/`
  and root `skills/` link to it
- `.claude/hooks/` — Claude-lifecycle-bound automation (rule 7)
- `docs/hooks/` — reserved for genuinely host-agnostic executables; empty
  today
- `docs/agents/` — the SSOT of agent definitions; `.claude/agents/` and
  `.agents/agents/` link to it

### related files

- [[adr-01-constitution]] — the written law this tooling serves
- [[adr-03-guardians]] — guardian agents and dispatch safety net
- [[adr-04-issue-delivery]] — issue → worktree → PR mechanics
- [[HARNESS]] — tooling section in prose
