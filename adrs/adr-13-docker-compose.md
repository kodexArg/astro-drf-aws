---
title: adr-13-docker-compose
type: adr
category: devops
use_case: editing compose.yaml, adding a service profile, changing a health check, touching backend/ or frontend/ app roots
created: 2026-07-10
modified: 2026-08-04
tags: [adr, docker, compose]
---

# ADR-13 — docker-compose and app paths

## CONTEXT

> Local orchestration is one root `compose.yaml`; app code is reserved to
> `backend/` and `frontend/` only.

Rules only; content lives in [[DOCKER]].

## ASSERTIONS

1. Reserved paths: application code for the two services lives under
   `backend/` and `frontend/` only. Those names are canonical
   ([[GLOSSARY]]). Creating alternate roots requires a new ADR.
2. Harness does not scaffold the apps beyond stage 3 project construction;
   agents must not invent `backend/` / `frontend/` application code unless
   the user asks for project construction.
3. Single Compose file: local orchestration is only repository-root
   `compose.yaml`. Per-app compose files are not the template default.
4. Dockerfiles sit in `backend/` and `frontend/` (two images / two Fargate
   services — [[INFRASTRUCTURE]]).
5. Profiles: `db`, `backend`, `frontend`, `full`.
6. No Redis in Compose ([[CACHE]]). Local DB is PostgreSQL 17 when `db`
   runs.
7. Env names from [[VARIABLES]]; `.env.example` is the committed local
   template — no secrets in git.
8. Health: db uses `pg_isready`. Backend/frontend probes (`/api/health/`,
   `/healthz`) apply per those services ([[API]], [[DOCKER]]).
9. Verification: `python3 tests/test_docker_compose.py` must pass.
10. Scope: Compose is local only. Production remains Fargate + ECR
    ([[INFRASTRUCTURE]]).

## RELATED

### related files

- [[adr-06-initial-stack]] — the stack Compose orchestrates locally
- [[DOCKER]] — full Compose doctrine
- [[INFRASTRUCTURE]] — production Fargate layout
- [[VARIABLES]] — env naming
- [[GLOSSARY]] — `backend`/`frontend` as canonical names
