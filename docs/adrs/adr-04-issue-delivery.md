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

Rules only; content lives in [[GH]]. This is this project's Claude-runtime
rendering of issue delivery — the sequence and diagrams live in
[[DEVELOPMENT-LOOP]].

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
