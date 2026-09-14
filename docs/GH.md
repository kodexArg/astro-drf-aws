---
title: GH
type: reference
status: active
created: 2026-07-10
tags: [harness, github, git]
---

# GH — GitHub + git for this template

Owner: **`kodexArg`**. Repo protocol: SSH. CLI: `gh` (used directly). Ruled by [[adr-12-github-and-git]].

## Branches

| Branch | Role |
|---|---|
| **`main`** | **Single line** — integration **and** production. Feature PRs merge here; every push to `main` may deploy to AWS. |
| **`prod`** | **Retired** for derived products. Historical only; do not open new promote PRs to `prod`. |

Forbidden: treating a second long-lived branch as production. Forbidden default branch name: `master` ([[GLOSSARY]]). Ruled by [[adr-29-permanent-deployment]].

## Who may push

- **Direct push to `main`:** account **`kodexArg` only**. (`prod` is retired for derived products.)
- Everyone else (agents, collaborators): **branches + PRs**. No direct push to protected lines.

## How we work

1. **Issues** for work tracking — open early, close with PR. Every issue uses a repository template from `.github/ISSUE_TEMPLATE/` — the BDD/Gherkin feature form is `gh-issue-feature-bdd.md` (chooser label "Feature (BDD)"); its References section is filled liberally so no issue is orphaned for want of a link graph.
2. **PRs** for every change that lands on `main`.
3. Agents open branches / PRs; they do not force-push `main` as another identity.
4. Base of feature PRs: **`main`**. There is no separate promote-to-`prod` step for derived products.

### The feature template at a glance (80-col view)

Annotated column-ruler view of `.github/ISSUE_TEMPLATE/gh-issue-feature-bdd.md`
(`!!` marks a line wider than the 80-col terminal — all prose/guidance, never
structure; GitHub wraps them):

```text
              1         2         3         4         5         6         7         8
     ....+....|....+....|....+....|....+....|....+....|....+....|....+....|....+....|
  1| ---                          ╮
  2| name: Feature (BDD)          │  frontmatter: name = chooser label in GitHub,
  3| about: ...                !! │  labels=feat, assignees=kodexArg, title prefix "feat: "
  4| title: "feat: "              │  (GitHub reads THIS, not the filename)
  5| labels: feat                 │
  6| assignees: kodexArg          │
  7| ---                          ╯
  9| <!-- ...                  !! ╮  author guidance: BDD-first, language, wikilinks,
 14| -->                          ╯  issue→PR loop. Not shown in the rendered issue.
 16| ## Story                     ╮  who / what / so-that + verbatim quote of the ask
 23| > "<...textual>"             ╯
 25| ## Scenario(s)               ╮  Gherkin Given/When/Then; comment invites a
 37| ```                          ╯  Scenario Outline for the negative cases
 39| ## Acceptance criteria       ╮  testable checklist; last row ties in
 43| - [ ] Shadow tests ...    !! ╯  shadow tests + guardian verdicts
 45| ## References  (star)        ╮  the star section: 4 link axes —
 47| <!-- #189 orphaned ...       │  Governing ADRs / Specs & docs / Code / Related.
 66| - [[informe-...]]            ╯  "link LIBERALLY" — born from the orphaned issue
 68| ## Notes / out of scope      ╮  what a fresh agent must NOT assume
 70| <!-- ... -->              !! ╯
```

## Labels (issues + PRs) — fixed set

Create only these; do not invent free-form labels.

| Label | Use |
|---|---|
| `bug` | Defect |
| `feat` | New capability |
| `chore` | Tooling, deps, noise cleanup |
| `docs` | Documentation / harness docs |
| `harness` | Skills, hooks, ADRs, agent config |
| `infra` | AWS, CI, deploy |
| `blocked` | Waiting on decision/input |

One primary type label per issue/PR; add `blocked` only when stuck.

## Git tags (releases)

- Format: **`vMAJOR.MINOR.PATCH`** (semver).
- Cut tags **from `main` only** after a production-ready land.
- Optional prerelease: `vX.Y.Z-rc.N` still from `main` (or a short-lived release branch merged to `main` first).

## CI / deploy refs

- **PR checks:** pull requests targeting `main`.
- **Production deploy + OIDC trust:** `refs/heads/main` only. Workflow `.github/workflows/deploy-prod.yml` triggers on `push` to `main`.
- No cloud `dev` environment and no second deploy ref for derived products ([[adr-29-permanent-deployment]]).
- Detail for AWS roles: [[INFRASTRUCTURE]].

### OIDC subject format — immutable IDs

Ruled by [[adr-24-oidc-immutable-subject-claim]]. GitHub repos **created, renamed, or transferred after 2026-07-15** emit their Actions OIDC `sub` claim in the **immutable subject format**, which appends the owner and repository numeric IDs — permanent identifiers a delete-and-recreate cannot reuse. There is no opt-out for such repos ([changelog 2026-04-23](https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/)).

| | `sub` format |
|---|---|
| Classic (pre-cutoff repos) | `repo:OWNER/REPO:ref:refs/heads/BRANCH` |
| Immutable (post-cutoff repos) | `repo:OWNER@OWNER-ID/REPO@REPO-ID:ref:refs/heads/BRANCH` |

Consequences that bind this template and every project spawned from it:

- An AWS trust-policy `sub` entry for a post-cutoff repo MUST use the immutable format; a name-only entry never matches and STS denies `AssumeRoleWithWebIdentity` with `Not authorized to perform sts:AssumeRoleWithWebIdentity`.
- Deleting and recreating a repo rotates its repo ID, so every trust entry for it must be re-derived — the name-only entry it had before is dead. This repo hit exactly that on its 2026-07-19 v1 history reset.
- Read a repo's live prefix with `gh api repos/OWNER/REPO/actions/oidc/customization/sub` (`sub_claim_prefix`). This repo's: `repo:kodexArg@47777332/astro-drf-aws@1305504992`.
- Repos born before the cutoff keep the classic format until they are recreated, renamed, or transferred — then they flip and their trust entries must follow.

> [!note] Permanent product deploy (derived clones)
> Derived products deploy production from `main`. There is no cloud `dev` environment and no second deploy ref. Secret ARNs, subnet IDs, and Cognito client IDs are filled **after bootstrap** — never invented, never copied from this template's live inventory. Ruled by [[adr-29-permanent-deployment]], [[adr-27-derived-project-deploy-identity]].
>
> Historical note: an optional template stage-3 experiment once used `refs/heads/prod` + ephemeral teardown ([[adr-15-ephemeral-run]]); that path is **superseded for clones** and must not be re-inherited.
