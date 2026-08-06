---
title: adr-15-ephemeral-run
type: adr
category: devops
use_case: provisioning any AWS resource for the reference deploy, running teardown, updating docs/INVENTORY.md
created: 2026-07-10
modified: 2026-08-05
tags: [adr, infrastructure, ephemeral, inventory]
---

# ADR-15 — the ephemeral reference run

## CONTEXT

> This template's own stage-3 reference deploy to `prod` is born dead: no
> resource may be assumed to survive.

Rules only; content lives in [[INFRASTRUCTURE]], [[BD]], [[GH]], and
[[VARIABLES]]. This ADR governs the template's own stage-3 reference deploy
of project `astro-drf-aws`; it does not change multi-project doctrine.

## ASSERTIONS

1. This run deploys to `prod` only. No cloud dev environment exists here:
   `main` is the local development line and `prod` is the only branch that
   reaches AWS. OIDC deploy trust is scoped to `refs/heads/prod` only. The
   `dev ← main` pipeline stays doctrine for real projects and is out of
   scope for this run ([[INFRASTRUCTURE]], [[GH]], [[adr-12-github-and-git]]).
2. The infrastructure is born dead. No document, code path, test, or step
   may depend on any provisioned resource surviving. Resources may serve for
   testing after the final okay, but only ever as ephemeral.
3. Every created resource carries the mandatory tag set owned by
   [[INFRASTRUCTURE]] — `project`, `env`, `lifecycle`. A resource missing any
   of the three is a defect, not a resource of this run.
4. This run provisions no database instance of its own. It takes a database
   and a login role on the shared `alvs-prod-pg` instance
   ([[adr-06-initial-stack]] rule 5 — no infrastructure divergence remains
   to sanction). The database and role names are derived from the project
   slug, never typed as literals, so a spawned project inherits the shape
   and not this run's name; the derivation, the specification, and the cost
   expectation are owned by [[BD]]. The instance itself is a shared resource
   under rule 6 and is never destroyed by teardown — Phase E drops only this
   project's database and role.
5. The inventory is committed and authoritative. `docs/INVENTORY.md` is
   updated in the same batch as each resource's creation, in the format
   owned by [[INFRASTRUCTURE]]; teardown executes from it and verifies
   against the Resource Groups Tagging API.
6. Shared pre-existing ALVS resources are never destroyed — only this
   project's attachments to them. The set of shared resources and the
   removable attachments are owned by [[INFRASTRUCTURE]].
7. Teardown is total and user-gated. Every `lifecycle=ephemeral` resource
   and every one of this project's secrets is destroyed in the order and
   manner owned by [[INFRASTRUCTURE]] — secrets die last, irrecoverably. The
   run is closed only when the Tagging API confirms zero `lifecycle=ephemeral`
   resources remain. Teardown never runs without kodex's explicit go in the
   current conversation.
8. This ADR is the standing ruling every stage-3 phase assumes active. It
   rules the sibling findings on deploy scope and RDS cost; those are
   resolved in their own batches through the findings protocol, never by
   amending this ADR in place beyond a genuine policy change.

## REJECTED

- **A dedicated ephemeral RDS instance for this run** — rule 4's policy from
  2026-07-10 until 2026-08-05: `alvs-prod-astro-drf-aws-pg`, a `db.t4g.micro`
  of its own, sanctioned as the infrastructure divergence
  [[adr-06-initial-stack]] rule 5 demands an ADR for. Retired by owner
  directive (2026-08-05): the run's database is ~9 MB and the shared
  `alvs-prod-pg` already hosts sibling projects the same way, so a whole
  instance bought isolation nobody needed at the price of the run's largest
  standing line item. The instance and its subnet group were destroyed in the
  same batch as this edit and the data moved to a database on the shared
  instance. It would reopen only if this run needed an engine version,
  parameter group, or maintenance window the shared instance cannot carry —
  none of which is a known need.

## RELATED

### related files

- [[adr-06-initial-stack]] — the shared-infrastructure rule this ADR no
  longer diverges from (rule 4)
- [[adr-12-github-and-git]] — the dev←main pipeline this run is exempt from
- [[adr-27-derived-project-deploy-identity]] — how a spawned project avoids
  inheriting this run's target
- [[INFRASTRUCTURE]] — tags, teardown order, shared resources
- [[BD]] — RDS spec and cost
- [[GH]] — OIDC trust scoping
- [[VARIABLES]] — variables this run reads
- [[INVENTORY]] — the committed resource ledger
