---
title: assertion-01-showcase-zero-props
type: reference
status: active
created: 2026-08-04
verified: 2026-08-04
tags: [assertion, frontend, componentization]
---

# Assertion-01 — every component mounts with zero props, safely

Every `.svelte` component under `frontend/src/lib/components/` — except a
component whose sole valid invocation is as a context-bound child of a
compound parent — MUST mount when invoked with zero props and MUST NEVER
throw doing so; and MUST NOT fire a mutating (`POST`/`PATCH`/`DELETE`)
`fetch` during that bare mount. This is [[adr-23-showcase-ready-components]]
rules 1–2 made verifiable: it is what lets any component be reused as-is in
both the gallery and a real page, with no forked showcase copy.

## RELATED

### Tests

- [component-mount.test.ts](../../frontend/tests/component-mount.test.ts) —
  self-discovers every `.svelte` file under `src/lib/components/`, mounts
  each with zero props asserting no throw, and asserts no mutating `fetch`
  fires on that bare mount; the `CONTEXT_BOUND` list carries the named,
  exact exemption for context-bound children. Green as of 2026-08-04 (`bun
  run test`, 817 pass / 0 fail).

### Files

- [component-mount.test.ts](../../frontend/tests/component-mount.test.ts)

### Docs

- [[adr-23-showcase-ready-components]]
- [[COMPONENTIZATION]]
- [[FRONTEND]]
