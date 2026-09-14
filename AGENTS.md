---
title: AGENTS
type: index
status: active
created: 2026-09-14
version: v0.1.0
tags: [harness, index, multi-runtime, team-party]
---

# AGENTS.md — harness entry point (Team Party)

**Template:** Astro 7 + Django 6 + two Fargate services. Product/PRD is hollow until a human fills `{{PLACEHOLDER}}` in [[PRD]] (`docs/constitution/PRD.md`) — **define the user** before inventing domains.

> [!info] Harness
> Team Party layout (mold `harness-team-party` + Fleet wiring). One real copy at repo root: `skills/`, `hooks/`, `agents/`, `adrs/`. Runtimes link: `.claude/{skills,hooks,agents,rules}`, `.agents/agents`, `.grok/skills`.

## ABC

1. Does it follow [[PRD]]? (`docs/constitution/PRD.md` — hollow slots are questions, not invented product)
2. Does it comply with active ADRs in `adrs/`?
3. Constitution / stack docs (`docs/constitution/`, [[INFRASTRUCTURE]], [[API]])
4. If backend surface: is it declared in [[API]]?

Hold PRD and API in memory. SessionStart `hooks/khook-load-ssot.py` preloads them when configured.

## Layout

| Path | Role |
|---|---|
| `adrs/` | All ADRs (stack + harness). `docs/adrs` → symlink |
| `agents/` | `kbot-*` guardians/workers + `kwf-*` cast + `souls/` |
| `hooks/` | `khook-*` (+ short-name compat symlinks for legacy tests) |
| `skills/` | `k-*` (Astro/Django/AWS + party skills) |
| `docs/constitution/` | Hollow PRD + INFRASTRUCTURE / REQUIREMENTS / … |
| `backend/`, `frontend/`, `compose.yaml` | Stack code |

## Party

Forest → tavern → camp (N slices) → stalking → plaza. Skill: `skills/k-triage-and-fix/`. Cast: `agents/kwf-*.md`. Guardians: `kbot-prd` / `kbot-adr` / `kbot-bdd` / `kbot-api`.

## Deploy doctrine

`main` → AWS prod ([[adr-29-permanent-deployment]]). Fill GitHub Actions vars after bootstrap — **never invent ARNs**. Shared Cognito org-pool + dedicated app client. No CDN. ECS circuit breaker with rollback. Detail: [[INFRASTRUCTURE]], [[GH]].

## Runtimes

- **Claude:** `.claude/{skills,hooks,agents,rules}` → root SSOTs. New session after harness swap.
- **Grok:** `.grok/skills` → `skills/`. Prefer `grok --cwd <clone>`.
- **Kimi:** point `extra_agent_dirs` at **this clone’s** `agents/`, never a sibling product.

Old `orch-*` / `astro-drf-aws-*` / `kdx-*` trees live under `docs/obsolete/harness-pre-team-party/` for archaeology only.
