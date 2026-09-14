# astro-drf-aws

Opinionated **stack template** (agnostic product). Owner: **kodexArg**.

- **Stack:** Astro **7** (SSR + Svelte) + Django **6** / DRF + **two** ECS Fargate services + shared ALB (**no CDN**)
- **Deploy doctrine:** `main` → AWS prod ([[adr-29-permanent-deployment]]); fill `REPLACE_AFTER_BOOTSTRAP` / GitHub Actions vars — **never invent ARNs**
- **Auth pattern:** shared Cognito org pool + dedicated confidential app client per project
- **Harness:** Team Party layout (`agents/` / `skills/` / `hooks/` / `adrs/`) — enter through [AGENTS.md](AGENTS.md)
- **PRD:** hollow `{{PLACEHOLDER}}` until a human owner defines the user and product ([docs/constitution/PRD.md](docs/constitution/PRD.md))

Local: `compose.yaml`. Danger brake for AWS: [DANGER-README-FIRST.md](DANGER-README-FIRST.md). Onboarding: [ONBOARDING.md](ONBOARDING.md).

| Branch | Role |
|--------|------|
| `main` | Integration **and** production (single line) |
| `prod` | Retired for derived products |
