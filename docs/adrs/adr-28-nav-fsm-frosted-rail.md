---
title: adr-28-nav-fsm-frosted-rail
type: adr
category: frontend
use_case: changing NavDrawer or FancyDrawer, adjusting shell menu visibility, lock or pin behavior, or the breakpoint that chooses rail vs drawer
created: 2026-08-05
modified: 2026-08-07
tags: [adr, frontend, shell, navigation, nav-fsm]
---

# ADR-28 — nav-fsm and the frosted locked rail

## CONTEXT

> The site menu has two modes — locked rail and unlocked drawer — and one of
> them must always be reachable. A viewport that cannot host the rail does
> not get to hide the menu. Preference and selection are known before first
> paint so navigation never blanks the chrome.

## ASSERTIONS

1. `NavDrawer` has exactly two presentation modes: **locked** (permanent
   in-flow rail) and **unlocked** (floating `overlay/FancyDrawer` with a peek
   caret). The user chooses the preference; the shell mounts one
   presentation at a time. Ownership of the components and the rail minimum
   width: [[COMPONENTIZATION]], [[DESIGN-SYSTEM]].
2. Locked mode is available only when the viewport meets the rail minimum
   width in [[DESIGN-SYSTEM]]. Below that width, the layout MUST present
   unlocked mode even if the lock preference is on; the preference persists
   so the rail returns when the viewport fits again.
3. The menu is NEVER invisible: wherever `NavDrawer` mounts, either the rail
   or the `FancyDrawer` peek caret is present and operable. A locked
   preference plus a CSS hide without an unlocked fallback is a defect.
4. The `FancyDrawer` peek caret toggles the drawer on click and tap as well
   as on mouse hover. When collapsed, the caret stays inside the drawer's
   hit box so pointer events reach it ([[COMPONENTIZATION]]).
5. Dock edge follows `theme_config.sidebarSide` ([[DESIGN-SYSTEM]], [[API]]).
6. Lock preference is a client chrome cookie (`nav_lock`), readable on SSR
   like the `theme` cookie, so the first byte of every navigation already
   knows locked vs unlocked. localStorage alone is not the source of truth.
   Mechanism: [[DESIGN-SYSTEM]].
7. `NavDrawer`'s runtime state is a closed FSM with three fields —
   preference (`locked`|`unlocked`), presentation (`rail`|`drawer`), and
   active item — resolved by `shell/nav-fsm`. Presentation is derived from
   preference alone and never stored; because both of its values are a menu,
   no FSM input can resolve to no menu (rule 3). The viewport band is **not**
   an FSM field: rule 2's floor is enforced by CSS at the rail minimum width
   over the pair rule 8 mounts, so nothing measured at runtime decides what
   renders. Active comes from the `pathname` prop `Base.astro` already passes
   ([[COMPONENTIZATION]]).
8. When preference is locked, first paint may mount both the rail and the
   drawer and let CSS at the rail minimum choose which is visible, so a full
   navigation cannot flash unlocked while JavaScript catches up.
9. The locked rail carries a soft wash and backdrop blur so a themed dotted
   background reads out of focus while nav labels stay sharp, and page
   content crossfades on navigation instead of hard-cutting; exact values
   and mechanism: [[DESIGN-SYSTEM]].

## FORBIDDEN

- **NEVER** hide the locked rail at a breakpoint without forcing unlocked
  `FancyDrawer` (rules 2–3). That pairing is how tablets lost the menu.
- **NEVER** leave the collapsed `FancyDrawer` caret outside the transformed
  element's hit box (rule 4). Paint without hit-testing is an invisible
  control.
- **NEVER** make lock preference depend on `onMount` / localStorage alone
  (rule 6). That blanks the locked rail on every Astro navigation until
  hydrate.
- **NEVER** reintroduce a runtime measurement into the FSM to choose the
  presentation (rule 7). Both presentations are a menu, CSS already
  enforces rule 2's floor, and a measured field can only start wrong and
  jump.

## REJECTED

- **`shell-nav-pinned` localStorage-only pin read in `onMount`** — the
  preference this template held before this ADR. Preference survived
  sessions but not SSR, so each link click painted unlocked then snapped to
  locked. Replaced by rule 6's `nav_lock` cookie; the legacy key is read
  once for a one-shot migration and then never written to again. Would
  reopen only if the menu stopped being SSR-mounted.
- **CSS hiding the rail below a breakpoint with no forced-drawer fallback**
  — never shipped in this template, but the precedent this ADR forbids
  outright (rules 2–3, FORBIDDEN) since it is exactly the defect the source
  design already hit once. Reopens only if a dedicated, always-wired open
  control replaces the forced-drawer fallback.
- **The viewport band as an FSM field** — `nav-fsm` carried a `viewport`
  (`mobile`|`tablet`|`desk`) resolved from two `matchMedia` listeners, and
  `resolvePresentation` took it as a second argument. Dropped 2026-08-07,
  owner authorization in conversation ([[adr-00-adr-doctrine]] rule 8): it
  decided nothing, because rule 8 already mounts rail and drawer together
  and CSS at the rail minimum picks the visible one. Its only effect was
  that presentation started at a guessed `desk` until `onMount` corrected
  it — a hydration jump bought with two listeners and a three-value type.
  Rule 2's floor is unchanged; it is enforced where it always actually was,
  in CSS. `DESK_MIN_WIDTH` (the Tailwind `lg` desk/tablet split) is dropped
  with it — it was informational only and had no consumer once viewport
  left the FSM. It would reopen only if a presentation decision genuinely
  needed a measurement no media query can express.

## RELATED

### related adrs

- [[adr-08-frontend-and-design-system]] — frontend stack this menu sits in
- [[adr-23-showcase-ready-components]] — zero-prop mount for `NavDrawer` and
  `FancyDrawer`
- [[adr-00-adr-doctrine]] — rule 8, the in-place policy change this ADR's
  rule 7 rewrite and REJECTED entry follow

### related files

- [[COMPONENTIZATION]] — `NavDrawer`, `FancyDrawer`, `NavLockToggle`,
  `shell/nav-fsm`
- [[DESIGN-SYSTEM]] — `sidebarSide`, the rail minimum width, the `nav_lock`
  cookie, and the frosted-rail/page-fade mechanism
- [[API]] — `theme_config.sidebarSide` on `PATCH /api/me/`
- [[GLOSSARY]] — `nav_lock` cookie, retired `shell-nav-pinned` key
