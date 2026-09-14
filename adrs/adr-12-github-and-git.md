---
title: adr-12-github-and-git
type: adr
category: devops
use_case: opening a PR, pushing to main or prod, cutting a release tag, applying a label to an issue or PR
created: 2026-07-10
modified: 2026-09-14
tags: [adr, github, git]
---

# ADR-12 — GitHub and git

## CONTEXT

> `main` is the single line (integration + production). Only `kodexArg`
> pushes it directly. The historical `prod` branch is retired for derived
> products ([[adr-29-permanent-deployment]]).

Rules only; content lives in [[GH]].

## ASSERTIONS

1. Owner is `kodexArg`. Remote and `gh` default owner follow that account.
2. `main` is the single line — integration and production both
   ([[adr-29-permanent-deployment]]).
3. The historical `prod` branch is retired for derived products; do not open
   new promote workflows to it.
4. Direct push to `main` is allowed only as `kodexArg`. All other work uses
   feature branches and pull requests.
5. Issues and PRs are the collaboration surface — no silent long-lived
   private workstreams that skip them when the change is shared or lands on
   `main`. [[adr-04-issue-delivery]] makes both mandatory per change: every
   change opens an issue first and reaches `main` only through a PR.
6. Feature PRs target `main`. There is no separate promote-to-`prod` step
   for derived products. Detail: [[GH]].
7. Labels are only the fixed set in [[GH]].
8. Release git tags are semver `v*`, cut from `main` only ([[GH]]).
9. CI/OIDC trust for production deploy is `refs/heads/main` only
   ([[INFRASTRUCTURE]], [[GH]], [[adr-29-permanent-deployment]]). A
   trust-policy `sub` entry for a repo created, renamed, or transferred
   after GitHub's immutable-subject cutoff MUST use the immutable subject
   format — owner and repository numeric IDs embedded; a name-only entry
   for such a repo is a defect, detailed in
   [[adr-24-oidc-immutable-subject-claim]].

## RELATED

### related files

- [[adr-04-issue-delivery]] — issue → worktree/branch → PR mechanics
- [[adr-24-oidc-immutable-subject-claim]] — immutable subject format detail
- [[GH]] — the full GitHub/git rules
- [[INFRASTRUCTURE]] — deploy targets per branch
