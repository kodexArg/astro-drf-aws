# DANGER — READ FIRST

> [!important] 2026-09-14 doctrine
> Derived products are **permanent** ([[adr-29-permanent-deployment]]): deploy from
> `main`, do **not** invent secret ARNs, do **not** mutate sibling FG/FM production
> AWS, do **not** treat ephemeral teardown as the default clone path.

This file is the template's **operator halt list**. Read it before any AWS write,
prod push, or secret touch.

## Standing guardrails

- **Never invent ARNs, VPC/SG/subnet IDs, or secret suffixes.** Fill
  `docs/INVENTORY.md` only with IDs returned by bootstrap (`REPLACE_AFTER_BOOTSTRAP`
  until then).
- **Never mutate sibling product AWS** (Financial Gateway / Fleet Management
  production). Those accounts and stacks are out of scope for this template.
- **Never force-push `main`.** Land changes via PR against `main`.
- **Never expose a secret value** in chat, commits, or logs.
- **Account and host are placeholders** until clone bootstrap:
  `{{AWS_ACCOUNT_ID}}`, `{{PUBLIC_HOST}}` / `{{BASE_DOMAIN}}`.
- Cost: do not create NAT, Redis/ElastiCache, Multi-AZ RDS, or extra ALBs
  unless the owner overrides in-turn.

## Halt (stop and ask a human)

- Any AWS resource create/delete outside the clone's own tagged stack.
- Any `prod` push or deploy the operator did not request.
- Any credential, account ID, or live ID copied from another product.
- Any invented-looking ARN used as an "example".

## After clone

1. Set `PROJECT_SLUG`, `BASE_DOMAIN` / `PUBLIC_HOST`, and `AWS_ACCOUNT_ID`.
2. Discover shared substrate (VPC, ALB, cluster) read-only; record real IDs.
3. Create project-owned resources; update INVENTORY in the **same batch**.
4. Keep PRD hollow (`{{PLACEHOLDER}}`) until the product user is defined.
