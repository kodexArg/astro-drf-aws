---
title: BD
type: reference
status: active
created: 2026-07-10
tags: [harness, database]
---

# BD

Database reference for the template. Engine: **PostgreSQL 17.9** (pin in [[REQUIREMENTS]]). Network placement, security groups, and bastion → [[INFRASTRUCTURE]]. Credentials as variables → [[VARIABLES]].

> [!note]
> Environments are **dev and prod only — no staging tier** in this account.

## prod

- RDS PostgreSQL **17.9**, instance `alvs-prod-pg`, class `db.t4g.micro`, **single-AZ**, in the isolated subnets ([[INFRASTRUCTURE]]).
- App credentials via Secrets Manager `alvs/prod/<project>/db` — JSON keys `host`, `port`, `dbname`, `username`, `password` — mapped to the discrete `DB_*` env vars ([[VARIABLES]]).
- Admin access **only** through the EICE bastion tunnel ([[INFRASTRUCTURE]]). The instance is never publicly reachable.

## dev (cloud)

- Identical pattern on `alvs-dev-pg`; secret `alvs/dev/<project>/db`.

## Naming — derived, never a literal

A project's database and role names are **derived from its slug**, so a project spawned from this template inherits the shape and never this template's name:

| Thing | Rule | This run |
|---|---|---|
| database | project slug, `-` → `_` | `astro_drf_aws` |
| login role | `<database>_user` | `astro_drf_aws_user` |

Hyphens stay out of SQL — a quoted identifier would have to be quoted at every call site forever. Typing either name as a literal in code, a workflow, or a task definition is a defect ([[adr-27-derived-project-deploy-identity]] rule 1): both reach the backend only as `DB_NAME`/`DB_USER` from `alvs/<env>/<project>/db` ([[VARIABLES]]).

## Ephemeral run DB (reference deploy)

Ruled by [[adr-15-ephemeral-run]] rule 4. The template's own run provisions **no instance of its own**: it takes a database and a role on the shared `alvs-prod-pg` above, exactly as the sibling ALVS projects do.

- Database `astro_drf_aws`, role `astro_drf_aws_user`, on `alvs-prod-pg` — created by the RDS master (`postgres`), which must first `GRANT <role> TO postgres` before it can own a database it does not itself own.
- The instance is a **shared** resource ([[INVENTORY]]) and is never destroyed. Phase E drops the database and the role, nothing more.
- **Cost expectation:** the run adds no instance-hour and no storage line of its own. Cost containment is that fact, not teardown timing.

## Admin access

Admin reaches an instance only from inside the VPC, through **SSM port-forwarding via the `monitor-prod-rds` box** — the one SSM-managed host whose SG the RDS SG admits on 5432:

```
aws ssm start-session --profile kodex --region us-east-1 \
  --target <monitor-prod-rds instance id> \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["<rds endpoint>"],"portNumber":["5432"],"localPortNumber":["15432"]}'
```

> [!warning] The EICE bastion cannot carry 5432
> An EC2 Instance Connect Endpoint accepts only ports **22 and 3389** as the remote port; `open-tunnel` straight at an RDS private IP is rejected with `InvalidParameter`. EICE reaches a database only by tunnelling SSH to an instance that then forwards. SSM is the shorter path and needs no key.

A local `pg_dump` newer than the server emits `SET transaction_timeout` (PG 18+), which a 17.9 server rejects — dump `--format=plain` and strip that line, or run the client at the server's major version.

## local (dev)

- Local PostgreSQL 17 (container or native), configured through the same discrete `DB_*` contract.
- Preferred container path: Compose service `db` via [[DOCKER]] (`docker compose --profile db up -d`).
- The code never knows which environment it's in — only the connection variables change.

## Rules

> [!important]
> **Django migrations are the ONLY schema mechanism.** No manual DDL, no external migration tools.

- One database per project per env.
- The cache table from [[CACHE]] lives in this same database — no separate cache store, Redis is prohibited.
- Engine version is pinned in [[REQUIREMENTS]]; re-pin follows that doc's policy.

## Migration execution points

- **Local:** the compose `backend` service runs `manage.py migrate` at startup ([[DOCKER]]) — dev convenience, single task, no race.
- **Cloud:** CI runs `migrate` as a **one-off ECS task before the service update**, never inside the service containers at startup — parallel tasks racing the same DDL is the failure mode this rule exists to prevent ([[INFRASTRUCTURE]] CI/CD).

## User identity

- User rows key on the Cognito `sub` claim — immutable, never recycled ([[GLOSSARY]]).
- User profile field names mirror Cognito standard attributes (`email`, `given_name`, `family_name`, …) so DRF serializers and Cognito claims share names with zero mapping. Auth doctrine: [[AUTH]].
