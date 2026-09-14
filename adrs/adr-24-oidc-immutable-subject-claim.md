---
title: adr-24-oidc-immutable-subject-claim
type: adr
category: devops
use_case: creating renaming or transferring a GitHub repo that deploys via OIDC, editing an OIDC trust policy, diagnosing a denied deploy role assumption
created: 2026-07-10
modified: 2026-08-04
tags: [adr, github, oidc, deploy]
---

# ADR-24 — immutable OIDC subject claims

## CONTEXT

> A repo created, renamed, or transferred after GitHub's immutable-subject
> cutoff needs the numeric-ID subject format — a name-only entry can never
> match.

Rules only; content lives in [[GH]] and [[INFRASTRUCTURE]]. This ADR adds to
[[adr-12-github-and-git]] rule 9; it narrows nothing else.

## ASSERTIONS

1. A CI/OIDC trust-policy `sub` entry for a GitHub repo created, renamed, or
   transferred after GitHub's immutable-subject cutoff MUST use the
   immutable subject format — owner and repository numeric IDs embedded. A
   name-only entry for such a repo is a defect: it can never match, and the
   deploy is denied. The format, the cutoff date, the lookup command, and
   this repo's live values are owned by [[GH]].
2. Recreating, renaming, or transferring a repo rotates its OIDC identity.
   Every trust entry naming that repo MUST be re-derived in the same batch
   as the change, and where the trust lives on a shared role, the mutation
   is recorded under the inventory discipline of [[adr-15-ephemeral-run]].
3. This is a doctrine addition, not a reversal: deploy refs, the
   branch→env mapping, and who may push ([[adr-12-github-and-git]]) are
   untouched.

## RELATED

### related files

- [[adr-12-github-and-git]] — rule 9, the deploy-trust scope this extends
- [[adr-15-ephemeral-run]] — inventory discipline for a shared-role mutation
- [[adr-27-derived-project-deploy-identity]] — rule 5, re-deriving the
  subject on a spawned project's own repo
- [[GH]] — format, cutoff date, lookup command, live values
- [[INFRASTRUCTURE]] — the trust policy this format binds
