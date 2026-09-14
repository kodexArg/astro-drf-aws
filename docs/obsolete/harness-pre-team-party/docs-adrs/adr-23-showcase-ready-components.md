---
title: adr-23-showcase-ready-components
type: adr
category: frontend
use_case: writing a new frontend component, deciding a component's default-invocation behavior, wiring a mutating action prop
created: 2026-07-10
modified: 2026-08-04
tags: [adr, componentization, showcase]
---

# ADR-23 — showcase-ready components

## CONTEXT

> Every component must render safely with zero props, and must never
> mutate anything by default.

Rules only; content lives in [[COMPONENTIZATION]], [[FRONTEND]],
[[DESIGN-SYSTEM]]. This ADR adds a component-contract requirement to
[[adr-08-frontend-and-design-system]]'s componentization rule; it narrows
nothing else.

## ASSERTIONS

1. Every frontend component MUST support invocation with zero props. Called
   with no required inputs, it renders a self-defined default or fallback
   state and MUST NEVER throw. How a component formats its own "no data"
   state is its own choice; erroring on an empty invocation is a defect
   regardless of that choice. The one exemption is a component whose only
   valid invocation is as a context-bound child of a parent compound
   component — never bare, by any caller: it may throw on a bare mount,
   because that throw states the parent requirement it exists to enforce.
   The parent itself is bound by this rule with no exemption. Enforcement of
   both halves — the requirement and the exemption's named, exact
   membership — is `frontend/tests/component-mount.test.ts` and its
   `CONTEXT_BOUND` list ([[COMPONENTIZATION]]).
2. A component's default invocation MUST NEVER perform a mutating action.
   With no caller-supplied action wiring, a component MUST NOT issue a
   mutating API call (POST/PATCH/DELETE), a navigation with session/state
   side effects, or a DB write. Any component capable of such an action
   takes it only through an explicit prop or callback supplied by the
   caller, and that prop MUST default to a safe no-op — or a clearly-labeled
   disabled/demo affordance — when the caller does not supply it. This is
   what lets a vendored component be reused as-is in both the gallery and
   real app pages with no forked showcase copy ([[COMPONENTIZATION]] —
   gallery-only demo compositions are compositions of real components, not
   substitutes for them).

## RELATED

### related files

- [[adr-08-frontend-and-design-system]] — the componentization rule this ADR
  extends (rule 9)
- [[COMPONENTIZATION]] — folder structure, `CONTEXT_BOUND` list, gallery
  compositions
- [[FRONTEND]] — component authoring rules
- [[DESIGN-SYSTEM]] — visual defaults
