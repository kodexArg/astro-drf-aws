---
title: adr-04-issue-delivery
type: adr
category: harness
use_case: opening a GitHub issue for a change, creating a worktree or feature branch, opening or merging a pull request, deciding who integrates to main or prod
created: 2026-07-10
modified: 2026-08-04
tags: [adr, harness, github, git, issue-delivery]
---

# ADR-04 — issue delivery (issue → worktree → PR)

## CONTEXT

> This project's delivery cast is manual git mechanics, not an automated
> multi-agent pipeline: every change opens an issue, moves through a
> worktree or feature branch, and reaches `main` only through a PR.

Rules only; content lives in [[GH]]. The manual git mechanics above (rules
1–6) are the baseline every change follows regardless of tooling; rule 7
below layers the harness-default cast and playbook on top as the
runtime-agnostic automation of that same shape — the sequence and diagrams
still live in [[DEVELOPMENT-LOOP]].

## ASSERTIONS

1. Every change enters through a `gh` issue — always, for everything, no
   matter how small. The issue is opened before the work, in this repo's own
   tracker ([[GH]]). A change with no issue is a change made by someone who
   did not read this ADR.
2. The pull request is the sole integration entry point. No change reaches
   `main` except by opening a PR and merging it; there is no direct
   hand-commit to `main` in the development flow. The worktree is optional —
   a plain feature branch → PR is the equal alternative; what is not
   optional is the PR.
3. Only the `gh`/kodexArg identity integrates, and in practice that is the
   agent — the sole holder of that credential. The merge to `main` is itself
   the kodexArg push authorized elsewhere ([[GH]]); this ADR routes that
   push through a PR, it does not remove the permission. No human hand-merges
   outside the `gh` identity. No second-party review is implied: the PR is
   record + gate, and self-merge is valid ([[GH]]).
4. The PR is the gate: the guardian verdicts ([[adr-03-guardians]]) and the
   test suites must be green before merge. Enforcement is layered and this
   ADR states its limit honestly: this doctrine is the rule, a local
   `PreToolUse` hook is a bypassable nudge, and the only inviolable backstop
   is GitHub branch protection, which lives in the repo of the moment and is
   therefore not shipped by this template. No document may state the PR as
   an unbypassable gate.
5. Integration destroys the worktree — always and explicitly. On merge the
   worktree is removed with `git worktree remove` (the agent/`-p` path does
   not auto-clean, so the removal is never left to an interactive prompt)
   and the branch is deleted. No worktree and no branch outlives its PR,
   whether the PR merged or was abandoned.
6. Boilerplate. The flow's terms enter [[GLOSSARY]] before first use; the
   step-by-step rendering and the exact commands stay in
   [[DEVELOPMENT-LOOP]], never here.
7. The `kwf-*` cast (`docs/agents/kwf-*.md` + `docs/agents/souls/`) and its
   playbook (`docs/skills/triage-and-fix/SKILL.md`) are the **canonical,
   runtime-agnostic SSOT** for what issue delivery through the party shape
   *is* — node contracts, phases, tiers ([[adr-02-harness]]). The pre-existing
   `docs/skills/kdx-wf-triage-and-fix` Workflow script over the `wf-*` cast is
   the **Claude-runtime rendering** of that same shape — Claude's
   schema-enforced structured-output Workflow primitive gives it a
   deterministic execution path the canonical cast does not require but this
   runtime happens to have. Neither supersedes the other; a run picks one
   cast and does not mix nodes across the two. Cross-runtime dispatch
   mechanics and model-tier mapping are owned by [[RUNTIMES]], never restated
   here.
8. The PR REQUIREMENT system layers onto rule 2's PR gate wherever a PR
   trusts another, unmerged PR rather than `main` alone: `requires:<N>` labels
   name the blocking PR(s); `deferred` marks a hunt called off, directly or
   by cascade, and is defined as the label being present **or** the PR being
   closed unmerged. `bin/kwf-deps` (`docs/skills/triage-and-fix/bin/kwf-deps`)
   is the sanctioned CLI for declaring, checking, cascading, and lifting these
   labels — a manual label edit that skips the cascade step is a defect,
   since a dependent PR left unlabeled after its requirement is deferred looks
   alive when its ground is gone. Full spec:
   `docs/skills/triage-and-fix/references/deps.md`.

## RELATED

### governed paths

- `.git/worktrees/` — created and destroyed per rule 5

### related files

- [[adr-00-adr-doctrine]] — the discipline this ADR obeys
- [[adr-01-constitution]] — where this ADR sits beneath the constitution
- [[adr-02-harness]] — skills/agents home this delivery flow uses
- [[adr-03-guardians]] — guardian verdicts as part of the PR gate (rule 4)
- [[adr-12-github-and-git]] — branches, labels, tags, who may push
- [[GH]] — GitHub/git specifics
- [[DEVELOPMENT-LOOP]] — the step-by-step rendering
- [[RUNTIMES]] — cross-runtime dispatch of the `kwf-*` cast (rule 7)
- `docs/skills/triage-and-fix/SKILL.md` — the canonical playbook (rule 7)
- `docs/skills/triage-and-fix/references/deps.md` — the REQUIREMENT/`deferred`
  spec (rule 8)
- `docs/skills/kdx-wf-triage-and-fix` — the pre-existing Claude Workflow
  rendering (rule 7)
