---
title: INVENTORY
type: reference
status: active
created: 2026-07-11
modified: 2026-09-14
tags: [infrastructure, aws, inventory, permanent]
---

# INVENTORY

Committed resource ledger. For **derived products**, every project-owned resource row is updated in the same batch as the change that creates or alters it ([[adr-29-permanent-deployment]]). Secret ARNs appear only after bootstrap — never invented.

> [!warning] Clones start empty of project rows
> A spawned repo inherits **no** project-owned inventory. Shared substrate rows below are **shape only** — fill IDs after discovery. Do not invent ARNs or copy another product's attachments. Do not treat historical `astro-drf-aws` demo rows as the clone's stack ([[adr-27-derived-project-deploy-identity]]).

The sections that follow document the **template inventory shape** (shared substrate + project-owned rows). Shared rows are never destroyed by a clone.

- Account `{{AWS_ACCOUNT_ID}}`, region `us-east-1`, profile `kodex` ([[INFRASTRUCTURE]]).
- `shared` = pre-existing org resource, never mutated beyond this project's own attachments; project-owned rows carry the mandatory tag set (`project={{PROJECT_SLUG}}`, `env=prod`, `lifecycle=…`) and are filled after bootstrap.

> [!note] Provenance
> Fill every `REPLACE_AFTER_BOOTSTRAP` cell from live discovery or create-output in the same batch as the change. Zero invented suffixes.

## Shared resources

| Resource | ID / ARN | Status | Recorded |
|---|---|---|---|
| VPC `alvs-prod` | `vpc-REPLACE_AFTER_BOOTSTRAP` (CIDR filled after discovery) | shared | after bootstrap |
| Subnet `alvs-prod-pub-1a` (public, us-east-1a) | `subnet-REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| Subnet `alvs-prod-pub-1b` (public, us-east-1b) | `subnet-REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| Subnet `alvs-prod-iso-1a` (isolated, us-east-1a) | `subnet-REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| Subnet `alvs-prod-iso-1b` (isolated, us-east-1b) | `subnet-REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| ECS cluster `alvs-prod` | `arn:aws:ecs:us-east-1:{{AWS_ACCOUNT_ID}}:cluster/alvs-prod` | shared | after bootstrap |
| Shared ALB `alvs-prod-alb` | `arn:aws:elasticloadbalancing:us-east-1:{{AWS_ACCOUNT_ID}}:loadbalancer/app/alvs-prod-alb/REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| ALB HTTPS listener (`:443`) | `arn:…:listener/app/alvs-prod-alb/REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| ALB HTTP listener (`:80`) | `arn:…:listener/app/alvs-prod-alb/REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| Route 53 zone `{{BASE_DOMAIN}}` | `/hostedzone/REPLACE_AFTER_BOOTSTRAP` (public) | shared | after bootstrap |
| GitHub OIDC provider | `arn:aws:iam::{{AWS_ACCOUNT_ID}}:oidc-provider/token.actions.githubusercontent.com` | shared | after bootstrap |
| Deploy role `gha-deploy-prod` | `arn:aws:iam::{{AWS_ACCOUNT_ID}}:role/gha-deploy-prod` | shared | after bootstrap |
| EICE bastion `alvs-prod-eice` | `eice-REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |
| Fargate task SG `alvs-prod-task-sg` | `sg-REPLACE_AFTER_BOOTSTRAP` | shared | after bootstrap |

### ALB HTTPS rule priorities (shape)

Used priorities on the `:443` listener are **project-owned host rules** for `{{PUBLIC_HOST}}` (direct ALB routing — no CDN) plus `default` (404). Keep path-pattern values within the 5-values-per-condition AWS quota; if `/accounts/*` cannot join the API rule, give auth its own higher-priority rule.

### Shared attachments this project may add (never the shared resource itself)

- Repo entry for this repo scoped to `refs/heads/prod` in the `gha-deploy-prod` trust policy. Use the immutable OIDC subject form when GitHub requires it ([[GH]], [[adr-24-oidc-immutable-subject-claim]]).
- Optional `bedrock:InvokeModel` statement on the deploy role if the live connectivity gate needs it — nothing wider.
- Host rule + target groups on the shared ALB for `{{PUBLIC_HOST}}`.
- Route 53 records under `{{BASE_DOMAIN}}`.

## Project-owned resources

Filled at bootstrap, one row per resource in the same batch as its creation; each carries the Article III tag set. Status stays `REPLACE_AFTER_BOOTSTRAP` until create-output is recorded.

| Resource | ID / ARN | Status | Recorded |
|---|---|---|---|
| Secret `alvs/prod/astro-drf-aws/django` | `arn:aws:secretsmanager:us-east-1:{{AWS_ACCOUNT_ID}}:secret:alvs/prod/astro-drf-aws/django-REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| Secret `alvs/prod/astro-drf-aws/db` | `arn:aws:secretsmanager:us-east-1:{{AWS_ACCOUNT_ID}}:secret:alvs/prod/astro-drf-aws/db-REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| Secret `alvs/prod/astro-drf-aws/cognito` | `arn:aws:secretsmanager:us-east-1:{{AWS_ACCOUNT_ID}}:secret:alvs/prod/astro-drf-aws/cognito-REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| Secret `alvs/prod/astro-drf-aws/s3` | `arn:aws:secretsmanager:us-east-1:{{AWS_ACCOUNT_ID}}:secret:alvs/prod/astro-drf-aws/s3-REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| Secret `alvs/prod/astro-drf-aws/msgraph` | `arn:aws:secretsmanager:us-east-1:{{AWS_ACCOUNT_ID}}:secret:alvs/prod/astro-drf-aws/msgraph-REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| Cognito user pool `alvs-prod-astro-drf-aws` | `REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | hosted-UI prefix must not contain the reserved word `aws`; test users `test-admin@example.com` / `test-user@example.com` (creds in the cognito secret only) |
| RDS subnet group `alvs-prod-astro-drf-aws-subnets` | isolated subnets `subnet-REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| RDS instance `alvs-prod-astro-drf-aws-pg` | `REPLACE_AFTER_BOOTSTRAP` — PostgreSQL 17.x, `db.t4g.micro`, single-AZ, private, sg `sg-REPLACE_AFTER_BOOTSTRAP`, db `app` | REPLACE_AFTER_BOOTSTRAP | — |
| S3 bucket `alvs-astro-drf-aws-media-prod` | private, all public access blocked | REPLACE_AFTER_BOOTSTRAP | — |
| ECR `alvs/astro-drf-aws-backend` | `{{AWS_ACCOUNT_ID}}.dkr.ecr.us-east-1.amazonaws.com/alvs/astro-drf-aws-backend` (immutable tags) | REPLACE_AFTER_BOOTSTRAP | — |
| ECR `alvs/astro-drf-aws-frontend` | `{{AWS_ACCOUNT_ID}}.dkr.ecr.us-east-1.amazonaws.com/alvs/astro-drf-aws-frontend` (immutable tags) | REPLACE_AFTER_BOOTSTRAP | — |
| IAM roles `alvs-prod-astro-drf-aws-{backend,frontend}-{exec,task}-role` | backend-exec: ECS exec policy + `GetSecretValue` on `alvs/prod/astro-drf-aws/*`; backend-task: media-bucket rw (+ Bedrock invoke if the assistant is enabled); frontend roles: exec policy only, **zero secret access** | REPLACE_AFTER_BOOTSTRAP | — |
| ACM cert `{{PUBLIC_HOST}}` | `arn:aws:acm:us-east-1:{{AWS_ACCOUNT_ID}}:certificate/REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| Route 53 record — ACM validation CNAME (host) | `REPLACE_AFTER_BOOTSTRAP` | shared-attachment | — |
| Route 53 A-alias `{{PUBLIC_HOST}}` → `alvs-prod-alb` | zone `REPLACE_AFTER_BOOTSTRAP` | shared-attachment | no CDN; private S3 + Django-issued presigned URLs |
| Target group `tg-astro-drf-aws-backend-prod` | `arn:…:targetgroup/tg-astro-drf-aws-backend-prod/REPLACE_AFTER_BOOTSTRAP` (HTTP 8000, hc `/api/health/`) | REPLACE_AFTER_BOOTSTRAP | — |
| Target group `tg-astro-drf-aws-frontend-prod` | `arn:…:targetgroup/tg-astro-drf-aws-frontend-prod/REPLACE_AFTER_BOOTSTRAP` (HTTP 4321, hc `/healthz`) | REPLACE_AFTER_BOOTSTRAP | — |
| Cloud Map namespace `astro-drf-aws-prod.local` | private DNS, VPC `alvs-prod` | REPLACE_AFTER_BOOTSTRAP | — |
| Cloud Map service `astro-drf-aws-backend` | `REPLACE_AFTER_BOOTSTRAP` | REPLACE_AFTER_BOOTSTRAP | — |
| ECS service `astro-drf-aws-backend` | `arn:aws:ecs:us-east-1:{{AWS_ACCOUNT_ID}}:service/alvs-prod/astro-drf-aws-backend` | REPLACE_AFTER_BOOTSTRAP | — |
| ECS service `astro-drf-aws-frontend` | `arn:aws:ecs:us-east-1:{{AWS_ACCOUNT_ID}}:service/alvs-prod/astro-drf-aws-frontend` | REPLACE_AFTER_BOOTSTRAP | — |
| Log groups `/alvs/astro-drf-aws/{backend,frontend}-prod` | retention 14 days | REPLACE_AFTER_BOOTSTRAP | — |
| VPC interface endpoint `com.amazonaws.us-east-1.bedrock-runtime` | not yet created — see note below | **planned** | `scripts/provision_bedrock_endpoint.sh`; tags on creation: `project=astro-drf-aws`, `env=prod` |
| Security group `alvs-prod-bedrock-vpce-sg` | not yet created — see note below | **planned** | ingress tcp/443 from `alvs-prod-task-sg` only |

> [!warning] Not provisioned until bootstrap (issue #95 shape)
> Run `scripts/provision_bedrock_endpoint.sh` with `AWS_ACCOUNT_ID`, `VPC_ID`, `TASK_SG_ID`, and `SUBNET_IDS` from discovery. Do not invent `vpce-*` / `sg-*` IDs. Flip the two planned rows in the same batch as creation.

> [!note] Permanent no-CDN routing
> This template ships without CloudFront (adr-02 r5). `{{PUBLIC_HOST}}` A-aliases directly to `alvs-prod-alb`. Media stays private S3 with Django-issued presigned URLs.
