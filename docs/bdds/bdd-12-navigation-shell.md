---
title: bdd-12-navigation-shell
type: bdd
status: building
created: 2026-08-01
tags: [bdd, frontend, nav, layout, design-system]
---

# bdd-12 — the navigation shell (layout-owned main, sticky header, edge drawers)

## Use case

As **any user with a role**, when I open any page, I get one continuous
canvas beneath a header that stays put while I scroll, so that a view is
*content resting on the canvas* rather than a component that happens to
declare itself the page. From a **tab at one edge of the viewport** I slide
out the **nav drawer** holding every route as its own item — icon, label,
and its pending-count badge where it has one — and from the **opposite
edge** I slide out the **chat drawer** hosting the page-context assistant
([[adr-25-page-context-assistant]]). Both drawers are **hidden by default**
and take no room until I ask for them; which edge the nav drawer docks to
is **mine to choose** on `/profile/`, and the chat drawer always takes the
opposite one. As a **role-less session**, I see neither drawer
([[adr-21-authorization-lobby]]).

This entry replaces the old navigation — `LobbyView`'s lobby cards as the
landing body, `HomeTriangle`, `CornerNavTriangle` (retired with
[[bdd-11-corner-nav-triangle]]) — with the shell: `PageCanvas`,
`LayoutHeader` + `NavBar`, `NavDrawer` + `ChatDrawer`, and the index page
`HomeCardsView`. It merges the two decisions the gateway proved out
separately — the layout owning `<main>` under a sticky in-flow header, and the
edge-docked drawers over a single nav registry — into the one shell the
template ships.

## Scenarios

### Exactly one landmark per page

```gherkin
Given any route rendered through Base.astro
When the document is parsed
Then it exposes exactly one <main> landmark
And that <main> comes from the layout (PageCanvas), not from a view component
And <header> is a sibling of it, keeping its banner landmark
And the page exposes exactly one <h1>, rendered by the NavBar chrome
```

### No view is a landmark any more

```gherkin
Given the view components under lib/components/views/
When their source is read
Then none of them renders a <main> element
And none of them declares min-h-screen
```

### The drawers are composed by the layout, role-gated

```gherkin
Given a signed-in user who holds at least one Django Group
When any route renders through Base.astro
Then the NavDrawer tab sits on the edge the theme field sidebarSide names (default left)
And the ChatDrawer tab sits on the opposite edge
And both drawers are collapsed, taking no room until their tab is used

Given a role-less session (anonymous or pending, [[adr-21-authorization-lobby]])
When any route renders
Then neither drawer is mounted
```

### Every nav item comes from the single registry

```gherkin
Given the NAV_ITEMS registry (frontend/src/lib/components/shell/nav.ts)
When the NavDrawer renders
Then every registry entry renders as a NavItem anchor with its href, label, and icon
And no nav item is authored anywhere outside the registry
And the item matching the current pathname carries the active state,
  decided by exact match after trailing-slash normalization
And no other item is active
```

## Frontend half

Rung 1 of the interactivity ladder for the canvas, header and links —
server-rendered HTML, plain anchors, no hydration; the drawers hydrate
only their open/close state (rung 3, as any click-reactive widget —
[[adr-08-frontend-and-design-system]] r3).

- **`PageCanvas`** (`primitives/`, new) — the single `<main>`: `flex-1`
  inside `body`'s app-shell flex column (`display: flex; flex-direction:
  column; min-height: 100dvh`), full width, **transparent**, and carrying
  **no header clearance**: the header is in-flow (`sticky`) and reserves
  its own space, so the canvas fills exactly what the header stack leaves.
  Composed by `Base.astro`; the layout never authors this markup inline
  ([[adr-08-frontend-and-design-system]] r9). `flex-1` rather than
  `min-h-dvh`: a full-viewport min-height below the in-flow header ends a
  header-height past the fold — the phantom scroll that pushed the
  standalone chat's composer off-screen — while long pages still stretch
  `body` past one viewport. Registered in [[GLOSSARY]] before first
  use ([[adr-05-glossary-and-localisation]] r1).
- **`LayoutHeader`** (`header/`) — keeps the **`banner` landmark** and is
  `sticky top-0 z-20` (never `fixed`): in-flow, so it reserves its own
  vertical space and no clearance token exists. It stays a **sibling** of
  `<main>`, never a child: a `<header>` nested inside `<main>` silently
  demotes from the `banner` landmark to a section header. It composes one
  `NavBar` and authors no chrome of its own.
- **`NavBar`** (`header/`, new) — the header's chrome: one `rounded-full`
  bar on the recessed surface ([[DESIGN-SYSTEM]]) spanning the header's
  width, **the page's single `<h1>`** at the left and the session island at
  the right through an `actions` snippet. The bar's title IS the page's
  `<h1>` — exactly one per page, authored in one place instead of per
  view; the views drop their own. It renders a `<div>`, never a `<nav>`,
  since it carries no navigation — those links are the `NavDrawer`'s.
  Zero props render an empty bar without throwing
  ([[adr-23-showcase-ready-components]] r1).
- **The view components** — `HomeCardsView`, `ChatView`, `ProfileView`,
  `ShowcaseGalleryView` — author **no `<main>` and no
  `min-h-screen` of their own**. They become content, not landmarks.
- **`NavDrawer`** (`shell/`, new — [[GLOSSARY]]) — the site nav drawer,
  composed once by `Base.astro` on the viewport edge the theme field
  `sidebarSide` names (default `left`), hidden until its tab is used.
  Every item is a `NavItem` over the single **`NAV_ITEMS` registry**
  (`frontend/src/lib/components/shell/nav.ts`) — `/chatui/`,
  `/showcase/components/`, `/profile/` with their labels, icons and badge
  keys; a second list anywhere would be a second authority that can
  disagree. **Active state** is exact match against the page's own
  pathname after **trailing-slash normalization**; the page passes its
  pathname in, the component does not read `window`, so it renders
  identically on the server. `NavItem` renders the project's own
  `ui/button` — `secondary` when active, `ghost` otherwise — so a nav link
  inherits the design system's focus, hover and radius tokens for free
  ([[DESIGN-SYSTEM]]); the icon comes from the caller, never resolved
  inside the component. `NavBadge` renders nothing when its count is zero
  or unknown.
- **`ChatDrawer`** (`shell/`, new — [[GLOSSARY]]) — the drawer composition
  mounting `ChatUI` with `mode="assistant"` inside `overlay/Drawer` on the
  **opposite edge** of `NavDrawer` — one theme field, two mirrored sides.
  A composition, not a widget, and never a second chat component:
  `ChatUI` is extended in place with the assistant mode, never forked
  ([[adr-25-page-context-assistant]], [[COMPONENTIZATION]]).
- **Both drawers are role-gated at the layout.** `Base.astro` mounts them
  only for a session holding at least one Django Group; a role-less
  session — anonymous or pending — sees neither
  ([[adr-21-authorization-lobby]] rule 1). The drawers perform no gating
  of their own.
- **`HomeCardsView` / `HomeCard`** (`views/`, new — [[GLOSSARY]]) — the
  `/` page body: one `HomeCard` per `NAV_ITEMS` entry (icon + title +
  abstract wrapped in a single navigating `<a>`, zero-prop-safe per
  [[adr-23-showcase-ready-components]] r1-2), plus the denied/pending
  lobby surfaces [[bdd-08-authorization-lobby]] defines. It replaces the
  retired `LobbyView`; the old `HomeTriangle`/`CornerNavTriangle`
  affordances are gone, their fronts now ordinary registry entries.
- **Zero-prop safety** ([[adr-23-showcase-ready-components]] r1): mounted
  bare, every new component renders its collapsed/empty default and throws
  nothing — `frontend/tests/component-mount.test.ts` covers them the
  moment they land (self-discovering glob, no list to update).
- **Variables consumed:** none. No `PUBLIC_*`, no fetch, no session read
  beyond what `Base.astro` already passes through ([[VARIABLES]]).

## Backend half

`sidebarSide` (`left`\|`right`, default `left`) joins the `theme_config`
closed key set validated by the `/api/me/` serializer — an out-of-enum
value a `400`, exactly as `bgPreset` is; it reuses the existing blob, its
cookie mirror and its `PATCH /api/me/` path. **No new [[API]] row** — no
route is added; but the blob's accepted keys grow, so [[API]]'s
`theme_config` validation paragraph MUST be updated in the same batch
([[adr-07-api-and-backend]] rule 1) — today it still lists the pre-shell
key set. No model field, no migration.

The assistant endpoint the `ChatDrawer` talks to is its own entry's
subject — `POST /api/assistant/ask/`, already declared in [[API]]
([[adr-25-page-context-assistant]]) — and is out of scope here.

## Error handling

No new failure surface on the shell itself: no fetch, no mutation, no
navigation beyond plain anchors. The zero-prop contract carries the
defensive requirement — `PageCanvas` with no props renders an empty,
valid `<main>`; `NavBar` an empty bar; the drawers collapsed on their
default edges — never throwing ([[adr-23-showcase-ready-components]] r1,
enforced by `frontend/tests/component-mount.test.ts`).

The one regression risk this entry names honestly: the canvas and the
in-flow header must together fill exactly one viewport — a full-viewport
min-height on the canvas re-introduces the phantom scroll (the standalone
chat's composer lands below the fold), and a `fixed` header would overlap
content nothing clears. `body`'s app-shell flex column plus `PageCanvas`'s
`flex-1` own both halves for every page, so the failure mode only returns
if a future page bypasses the layout — which
[[adr-08-frontend-and-design-system]] r9 already forbids.
`Cache-Control` remains each route's own concern, unchanged ([[CACHE]]).

## Shadow-test spec

- `frontend/tests/component-mount.test.ts` — zero-props mount of every new
  shell/header/primitives/views component, no throw, no mutating fetch
  (adr-22 r1/r2), covered by the suite's existing glob (no manual list
  entry needed).
- Every route rendered through `Base.astro` exposes exactly one `<main>`
  (from `PageCanvas`), a sibling `<header>` keeping its `banner` landmark,
  and exactly one `<h1>` (from `NavBar`); no view component renders a
  `<main>` or declares `min-h-screen`.
- Given the three `NAV_ITEMS` entries, three anchors render, each with its
  `href`, its label, and its icon; the item matching the supplied pathname
  carries the active state after trailing-slash normalization, and no
  other does.
- A `theme_config` carrying `sidebarSide: "top"` is rejected `400`;
  `left` and `right` round-trip through `PATCH /api/me/` and the `theme`
  cookie.
- A role-less session's pages mount neither drawer tab; a role-holding
  user's pages mount both, on opposite edges.
- Real-browser flow, `kodex`-only, via `chrome-devtools` MCP ([[AGENTS]]):
  open `/`, confirm the header stays put through a long scroll and exactly
  one `<h1>` is present; click the nav-drawer tab, click an item, land on
  it with its active state shown; open the chat drawer from the opposite
  edge; flip `sidebarSide` on `/profile/` and confirm both drawers mirror
  to the other pair of edges.
- Until a project's shadow-test runner exists, this entry may reach
  `building`, never `shipped` ([[BDD]]).
