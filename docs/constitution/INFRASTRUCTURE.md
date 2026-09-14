---
title: INFRASTRUCTURE
type: reference
status: active
created: 2026-07-10
tags: [harness, infrastructure, aws]
---

# INFRASTRUCTURE

AWS layout for the Astro SSR + DRF pair: **two Fargate services** per project, region **us-east-1**, ALVS account. Conventions mirror the ALVS production precedent (Financial Gateway / Fleet). `<project>` / `{{PROJECT_SLUG}}` is the placeholder for the project slug — carried at runtime by `PROJECT_SLUG` ([[VARIABLES]]). Public host is **`{{PUBLIC_HOST}}`** (owner-chosen; **not** necessarily `<slug>.{{BASE_DOMAIN}}`).

> [!important] Derived products are permanent
> Clones follow [[adr-29-permanent-deployment]]: `lifecycle=permanent`, deploy from **`main`**, fill secret ARNs only after bootstrap. Do **not** invent ARNs; do **not** reuse this template's live attachments as the clone's stack ([[adr-27-derived-project-deploy-identity]]).

> [!note]
> Derived products: **prod from `main` only** — no cloud `dev` tier by default. Local development uses Compose ([[DOCKER]]).

Database specifics → [[BD]]. Variable and secret contents → [[VARIABLES]]. Cache behavior → [[CACHE]]. Version pins → [[REQUIREMENTS]].

## ECS

- One cluster per env: `alvs-dev`, `alvs-prod`.
- Two services per project: `<project>-backend`, `<project>-frontend`.
- Launch type Fargate, network mode `awsvpc`.
- Baseline sizing: **256 CPU / 512 MB**, `desiredCount: 1`. Scale up only when measured.

## Networking

- One VPC per env: dev `10.10.0.0/16`, prod `10.20.0.0/16`. Two AZs each.
- **Public subnets**: ALB + Fargate tasks (tasks get public IPs).
- **Isolated subnets**: RDS only ([[BD]]).

> [!warning]
> **No NAT gateways — deliberate cost trade-off.** Tasks reach the internet through their public IPs. This diverges from the textbook private-subnet layout on purpose. Do not "fix" it by adding NAT.

### Accepted risk: public task IPs

Consequent to the no-NAT trade-off above, every Fargate task — the backend and frontend services **and** the one-off migrate task — is launched with `assignPublicIp=ENABLED` into the public subnets (`deploy-prod.yml`: `PUBLIC_SUBNET_A`/`PUBLIC_SUBNET_B`, the `awsvpcConfiguration` built for the migrate task run and reused for the service network configs). This is a **deliberate, accepted cost trade-off**, not an oversight — do not read it as a security bug or "fix" it unilaterally.

> [!warning] Accepted risk, not a finding
> Task ENIs are internet-routable, and the task security group (`alvs-<env>-task-sg`) is the sole isolation layer — no NAT, no private subnet, no network ACL beyond the SG. The migrate task in particular carries `DB_PASSWORD` and `SECRET_KEY` as env secrets while holding a public IP. The trade-off is accepted for cost reasons consistent with the "No NAT gateways" decision immediately above; it is not silently accepted risk, it is documented accepted risk.

**Contrast and optional future path.** Isolated subnets already exist for this project, RDS-only today (`alvs-prod-iso-1a` / `alvs-prod-iso-1b`, [[INVENTORY]]). A future hardening — moving Fargate tasks into isolated subnets with `assignPublicIp=DISABLED`, plus VPC interface endpoints for ECR, Secrets Manager, and CloudWatch Logs (mirroring the Bedrock endpoint pattern below) — is named here as optional future work. It is not silently precluded, but it is out of scope for this note and requires its own issue and engagement with this file's ownership ([[adr-06-initial-stack]] rule 5) before it is pursued.

### Bedrock VPC interface endpoint

- **`com.amazonaws.us-east-1.bedrock-runtime`** interface endpoint, one per env, placed in that env's **public subnets** (the same subnets the Fargate tasks run in — this stack has no isolated/private application subnet; RDS's isolated subnets are DB-only and out of scope here).
- **Private DNS enabled** — the backend resolves `bedrock-runtime.us-east-1.amazonaws.com` to the endpoint's private ENIs with zero code change ([[BACKEND]], async wrap per [[adr-18-async-mandatory]] rule 4).
- Security group `alvs-<env>-bedrock-vpce-sg` — ingress tcp/443 from `alvs-<env>-task-sg` only; interface endpoints originate no outbound connections, so no egress rule is required.
- Purpose: lets the backend reach Bedrock without a NAT gateway, keeping the no-NAT trade-off above and [[adr-06-initial-stack]] rule 5 intact — this is the private-networking path Bedrock inference needs instead of public-IP egress.

## Containers

| Component | Port | Runtime | Repo path |
|---|---|---|---|
| backend | 8000 | ASGI ([[BACKEND]]) | `backend/` |
| frontend | 4321 | Astro SSR, host `0.0.0.0` ([[FRONTEND]]) | `frontend/` |

Local images and Compose: [[DOCKER]] (root `compose.yaml` only; Dockerfiles under each path).

## ECR

- Repos: `alvs/<project>-backend`, `alvs/<project>-frontend`.
- Image tags: `<env>-<full-git-sha>`. No `latest`, no mutable tags.

## ALB

- One **shared** internet-facing ALB per env: `alvs-<env>-alb`. Every project on the env rides the same ALB via host rules.
- `:80` → redirect to `:443`. TLS 1.3 policy on `:443`.
- Default action: **404** for unknown hosts.
- One host per project: **`{{PUBLIC_HOST}}`** (prod). Optional cloud-dev host only if the owner opens a separate issue; default is none.
- Path rules, by priority, route to the **backend** target group:
  1. `/accounts/*`
  2. `/ws/*`
  3. `/api/*`
  4. `/admin/*`
  5. `/static/*`
  6. `/media/*`
- Catch-all for the host → **frontend** target group.
- Target groups: `tg-<project>-<component>-<env>`.

## Service discovery

- Cloud Map private DNS namespace per project per env: `<project>-<env>.local`.
- Frontend SSR calls hit the backend at `backend.<project>-<env>.local:8000` — the service segment is the bare `CLOUDMAP_SERVICE` value (`backend`), not `<project>-backend`.
- When frontend and backend share one task SG, add a self-referencing ingress rule on tcp/8000 (record the rule id in [[INVENTORY]] after bootstrap — **never invent** it).

> [!important]
> SSR-to-backend traffic goes through Cloud Map only — **never via the public ALB**.

The backend's `ALLOWED_HOSTS` ([[VARIABLES]]) **must include the Cloud Map hostname** (`backend.<project>-<env>.local`) **in addition to** `{{PUBLIC_HOST}}`, or Django rejects the SSR fetch as `DisallowedHost`. Example shape: `backend.{{PROJECT_SLUG}}-prod.local,{{PUBLIC_HOST}}`.

## Secrets

- **AWS Secrets Manager only.** No SSM Parameter Store.
- Naming scheme: `{{org}}/<env>/<project>/{db,django,cognito,s3,…}` JSON blobs; task definitions pull individual keys.
- Frontend tasks receive plain `PUBLIC_*` env only — **zero secrets**.
- Opaque AWS-assigned secret ARN suffixes are **not** a pure function of `PROJECT_SLUG`. Fill `SECRET_*` in the deploy workflow / GitHub Actions vars only **after bootstrap** (`REPLACE_AFTER_BOOTSTRAP`). **Never invent ARNs.** **Never copy** sibling-product or template-demo ARNs into a clone ([[adr-27-derived-project-deploy-identity]], [[adr-29-permanent-deployment]]).
- The variables themselves are declared in [[VARIABLES]] — the SSOT.

> [!warning] Shared Cognito org-pool pattern
> Authentication uses the shared org user pool (pattern name: **`alvs-org-pool`**) plus a **dedicated confidential app client per project**. Pool id, client id, client secret, and hosted-UI domain live only in Secrets Manager at `{{org}}/<env>/<project>/cognito` — never as committed defaults. Do not point a clone at a historical project-named pool leftover from this template's demo. Callbacks: `https://{{PUBLIC_HOST}}/accounts/callback/`. Detail: [[AUTH]].

## Logs and IAM

- CloudWatch log groups: `/alvs/<project>/<component>-<env>`, stream prefix = env.
- IAM roles: `alvs-<env>-<project>-<component>-{exec,task}-role`.
- Optional Bedrock/router grants are product-optional; if used, scope `bedrock:InvokeModel` to the specific model/profile ARNs — never `bedrock:*`. Model access in the Bedrock console is separate from IAM.

## DNS

- **No CDN.** The user-facing host (`{{PUBLIC_HOST}}`) A-aliases directly to the shared ALB — deliberate: these are internal, authenticated apps whose content is not edge-cacheable.
- Media: private S3 bucket `alvs-<project>-media-<env>`, never public; Django issues short-lived presigned URLs per object ([[BACKEND]]).
- Statics: served directly by the backend container behind the ALB `/static/*` rule ([[BACKEND]]).
- Cache behavior rules live in [[CACHE]].

## CI/CD

- GitHub Actions with **OIDC** (`token.actions.githubusercontent.com`) — no long-lived AWS keys.
- Shared deploy role name (ALVS substrate): `gha-deploy-prod` — document as **reuse substrate**; trust entries are per-repo. `sub` entries for repos created/renamed/transferred after GitHub's immutable-subject cutoff use the immutable format with owner/repo numeric IDs — format and procedure in [[GH]] ([[adr-24-oidc-immutable-subject-claim]]). **Do not invent** owner/repo numeric IDs; read the live prefix with `gh api`.
- **Branch → env (derived products):** `refs/heads/main` → **prod** deploy only. No cloud `dev` environment by default. Ruled by [[adr-29-permanent-deployment]], [[adr-12-github-and-git]], [[GH]].
- Direct push to `main` is `kodexArg` only; CI still runs on that ref after land.
- Pipeline shape: test → (optional connectivity gates) → build/push ECR → one-off Fargate RunTask migrate → register task defs → update ECS services → `aws ecs wait services-stable`.

### ECS deployment circuit breaker (mandatory)

Both `<project>-backend` and `<project>-frontend` services **must** enable the ECS deployment circuit breaker **with rollback**:

```text
deploymentConfiguration.deploymentCircuitBreaker = { enable=true, rollback=true }
```

A failed roll-forward restores the previous task definition. Operators recover by fixing the image/config and re-pushing `main` — do not invent one-off mutate scripts against sibling products' AWS. Documented also in the deploy workflow comments and the containers skill.

## Security groups

Chain, strictly one-directional:

1. `alvs-<env>-alb-sg` — public 80/443.
2. `alvs-<env>-task-sg` — ingress from the ALB SG only. When frontend and backend tasks share one task SG, the SSR-to-backend Cloud Map call additionally needs a self-referencing ingress rule (task SG → itself, tcp/8000).
3. `alvs-<env>-rds-sg` — 5432 from the task SG only.

DB admin access goes through an **EC2 Instance Connect Endpoint bastion** — see [[BD]]. Network IDs (`PUBLIC_SUBNET_*`, `TASK_SG_ID`) are bootstrap-filled — never invent them in the template workflow.

## Deployment lifecycle (derived products)

Force: [[adr-29-permanent-deployment]]. Two-Fargate layout: this file's ECS and networking sections.

- **Cloud scope: prod from `main`.** No cloud `dev`. OIDC deploy trust is `refs/heads/main` only.
- **Mandatory tag set** on every project-created resource:

  | Tag key | Value | Purpose |
  |---|---|---|
  | `project` | `{{PROJECT_SLUG}}` | scoping / cost attribution |
  | `env` | `prod` (or declared env) | environment |
  | `lifecycle` | `permanent` | derived products are not born dead |

- **Inventory:** `docs/INVENTORY.md` is the committed record. Update it in the **same batch** as each resource create/alter. Secret ARNs appear only after bootstrap.
- **Shared ALVS substrate is never destroyed** — VPC, ECS cluster, shared ALB, Route 53 zone, the GitHub OIDC provider, `gha-deploy-prod`, shared RDS, shared Cognito org pool, the EICE bastion. Only this project's additive attachments may ever be removed (owner-gated issue — not a standing teardown routine).
- Historical template demo / ephemeral teardown notes live under the superseded [[adr-15-ephemeral-run]]; **clones must not inherit teardown-as-routine**.
