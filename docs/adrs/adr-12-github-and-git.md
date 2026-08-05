---
title: adr-12-github-and-git
type: adr
category: devops
use_case: opening a PR, pushing to main or prod, cutting a release tag, applying a label to an issue or PR
created: 2026-07-10
modified: 2026-08-04
tags: [adr, github, git]
---

# ADR-12 — GitHub and git

## CONTEXT

> `main` is integration, `prod` is production, and only `kodexArg` pushes
> those lines directly.

Rules only; content lives in [[GH]].

## ASSERTIONS

1. Owner is `kodexArg`. Remote and `gh` default owner follow that account.
2. `main` is integration, not production.
3. `prod` is the production branch.
4. Direct push to `main` and `prod` is allowed only as `kodexArg`. All other
   work uses feature branches and pull requests.
5. Issues and PRs are the collaboration surface — no silent long-lived
   private workstreams that skip them when the change is shared or lands on
   `main`/`prod`. [[adr-04-issue-delivery]] makes both mandatory per change:
   every change opens an issue first and reaches `main` only through a PR.
6. Feature PRs target `main`. Promotions to production target `prod` (from
   `main` or an agreed release head). Detail: [[GH]].
7. Labels are only the fixed set in [[GH]].
8. Release git tags are semver `v*`, cut from `prod` only ([[GH]]).
9. CI/OIDC trust for deploy: dev ← `main`, prod ← `prod` ([[INFRASTRUCTURE]],
   [[GH]]). A trust-policy `sub` entry for a repo created, renamed, or
   transferred after GitHub's immutable-subject cutoff MUST use the
   immutable subject format — owner and repository numeric IDs embedded; a
   name-only entry for such a repo is a defect, detailed in
   [[adr-24-oidc-immutable-subject-claim]].

## RELATED

### related files

- [[adr-04-issue-delivery]] — issue → worktree/branch → PR mechanics
- [[adr-24-oidc-immutable-subject-claim]] — immutable subject format detail
- [[GH]] — the full GitHub/git rules
- [[INFRASTRUCTURE]] — deploy targets per branch
