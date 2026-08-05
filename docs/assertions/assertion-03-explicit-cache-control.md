---
title: assertion-03-explicit-cache-control
type: reference
status: active
created: 2026-08-04
verified: 2026-08-04
tags: [assertion, backend, cache]
---

# Assertion-03 — every response carries an explicit Cache-Control header

Every response the backend emits MUST carry an explicit `Cache-Control`
header — an absent header is a bug, never a default
([[adr-10-cache]] rule 3). The health endpoint, which serves no
personalized data, MUST set `Cache-Control: no-store`.

## RELATED

### Tests

- [tests.py::test_health_sets_explicit_cache_control](../../backend/apps/health/tests.py) —
  asserts `GET /api/health/` responds with `Cache-Control: no-store`.

Runs and passes as of 2026-08-04 (`uv run pytest
apps/health/tests.py::test_health_sets_explicit_cache_control`; 1 passed,
no database required).

### Files

- [backend/apps/health/views.py](../../backend/apps/health/views.py)

### Docs

- [[adr-10-cache]]
- [[CACHE]]
