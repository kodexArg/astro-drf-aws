---
title: CLONE-DRY-RUN
type: reference
status: active
created: 2026-09-14
tags: [onboarding, bootstrap, aws, template]
---

# Clone dry-run checklist (docs only)

Walkthrough for a **new repo from this template**. Do **not** execute against FG/FM production AWS. Fill placeholders after bootstrap — **never invent ARNs**.

## 0. Define the user

1. Open `docs/constitution/PRD.md` and replace every `{{PLACEHOLDER}}` with the owner.
2. Do not invent domains, roles, or acceptance criteria before the user is defined.

## 1. Identity

| Slot | Where | Notes |
|------|-------|-------|
| `PROJECT_SLUG` | GitHub Actions `vars`, `.env`, compose | Set once; not a sibling product's slug |
| `PROJECT_HOST` / `{{PUBLIC_HOST}}` | vars + DNS | Owner-chosen; **not** necessarily `<slug>.domain` |
| `BASE_DOMAIN` | vars | e.g. org domain |
| OIDC trust | IAM `gha-deploy-prod` | `refs/heads/main` only; read live immutable `sub` via `gh api` — do not invent owner/repo IDs |

## 2. Cognito (org-pool pattern)

1. Reuse shared org pool (pattern: `alvs-org-pool`).
2. Create a **dedicated confidential app client** for this project.
3. Callbacks: `https://{{PUBLIC_HOST}}/accounts/callback/`.
4. Store pool id / client id / secret / domain in Secrets Manager `{{org}}/prod/{{PROJECT_SLUG}}/cognito` only — never as committed defaults.

## 3. Secrets Manager

Create JSON blobs (names scheme only — suffixes are opaque):

- `{{org}}/prod/{{PROJECT_SLUG}}/django`
- `{{org}}/prod/{{PROJECT_SLUG}}/db`
- `{{org}}/prod/{{PROJECT_SLUG}}/cognito`
- optional: `s3`, integrations — only if opted in

Copy the **full ARNs after create** into GitHub Actions repository variables (`SECRET_DJANGO`, `SECRET_DB`, `SECRET_COGNITO`, …). Never invent the random suffix.

## 4. Network / ECS / ALB

1. Reuse shared VPC, cluster, ALB, task SG (record IDs in `docs/INVENTORY.md` after discovery — do not invent).
2. Set `PUBLIC_SUBNET_A/B`, `TASK_SG_ID`, `CLUSTER`, `ECR_REGISTRY`, `AWS_ACCOUNT_ID`, `DEPLOY_ROLE_ARN` as repository vars.
3. Create ECR repos `alvs/{{PROJECT_SLUG}}-backend|frontend`.
4. Create ECS services `{{PROJECT_SLUG}}-backend|frontend` with **circuit breaker + rollback** enabled.
5. Add ALB host rules for `{{PUBLIC_HOST}}` (path prefixes → backend TG; catch-all → frontend TG).
6. Cloud Map namespace `{{PROJECT_SLUG}}-prod.local`; ensure `ALLOWED_HOSTS` includes `backend.{{PROJECT_SLUG}}-prod.local`.
7. DNS: A-alias `{{PUBLIC_HOST}}` → shared ALB (**no CDN**).

## 5. First deploy

1. Confirm `deploy-prod.yml` triggers on `push` to `main`.
2. `check-bootstrap` must pass (fail-closed if vars missing).
3. Pipeline: test → build/push → migrate RunTask → register task defs → update services → `services-stable`.
4. On failed roll-forward, ECS restores previous task def (circuit breaker).

## 6. Inventory

Update `docs/INVENTORY.md` in the **same batch** as each create/alter. Clones start with **no** project-owned rows.

## Out of scope here

- Mutating FG or FM production resources
- Standing up live AWS without an owner issue
- Copying this template's historical demo ARNs into the clone
