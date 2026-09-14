---
title: adr-29-permanent-deployment
type: adr
status: active
created: 2026-09-14
version: v0.1.0
tags: [adr, aws, deploy, lifecycle, prod]
paths:
  - "docs/constitution/INFRASTRUCTURE.md"
  - "docs/INFRASTRUCTURE.md"
  - "docs/INVENTORY.md"
  - ".github/workflows/deploy-prod.yml"
related_adrs:
  - "adr-00-adr-doctrine"
  - "adr-06-initial-stack"
  - "adr-12-github-and-git"
  - "adr-15-ephemeral-run"
  - "adr-24-oidc-immutable-subject-claim"
  - "adr-27-derived-project-deploy-identity"
description: "Establishes derived products as permanent production deployments from main. Forbids treating clone infrastructure as ephemeral-by-default, reusing this template's live attachments, or inventing secret ARNs."
applies_when: "Creating, tagging, or destroying an AWS resource, wiring OIDC deploy trust, editing the inventory, or spawning a product from this template. Triggers: lifecycle=permanent, teardown, INVENTORY, deploy from main, shared substrate, gha-deploy-prod, REPLACE_AFTER_BOOTSTRAP."
---

# ADR-29 — the permanent production deployment

Rules only; content lives in [[INFRASTRUCTURE]], [[INVENTORY]], [[BD]], [[AUTH]], [[GH]]. **Derived products** (repos spawned from this template) are permanent production deployments unless the owner opens a separate issue deciding otherwise. This ADR supersedes [[adr-15-ephemeral-run]] for every derived product. The template's own optional demo run, if any, is never the default path a clone inherits.

1. Derived-product infrastructure is permanent. Every resource a derived product creates carries `lifecycle=permanent`; no document, test, or step may assume or require a teardown. Destroying that project's resources would be a new, owner-gated decision entering through its own issue, never a standing routine.
2. Deploys reach AWS from `main` only, on every push to it. `main` is the single line — integration and production both — and OIDC deploy trust stays scoped to `refs/heads/main` ([[GH]], [[adr-12-github-and-git]], [[adr-24-oidc-immutable-subject-claim]]). No cloud dev environment exists for a derived product by default, and no second ref holds deploy trust.
3. The mandatory tag set stands: `project={{PROJECT_SLUG}}`, `env`, `lifecycle` on every project resource ([[INFRASTRUCTURE]]). A resource missing any of the three is a defect.
4. [[INVENTORY]] remains committed and authoritative: every resource row is updated in the same batch as the change that creates or alters it. Secret ARNs are filled only after bootstrap (`REPLACE_AFTER_BOOTSTRAP`), **never invented**, and **never taken** from this template's live attachments or from sibling products (Financial Gateway, Fleet, etc.).
5. Shared ALVS substrate is reused, never mutated destructively. A derived product rides the shared cluster, ALB, VPC, shared RDS instance (or an owner-authorized new FreeTier PG), and the shared Cognito **org pool** plus a **dedicated app client per project** ([[BD]], [[AUTH]], [[INFRASTRUCTURE]]); only that project's own additive attachments may ever be removed. Template leftovers under `astro-drf-aws` are **not** the clone's stack ([[adr-27-derived-project-deploy-identity]]).
6. Any change to rules 1–5 is semantic and MUST supersede this ADR ([[adr-00-adr-doctrine]]).
