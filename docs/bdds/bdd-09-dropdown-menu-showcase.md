---
title: bdd-09-dropdown-menu-showcase
type: bdd
status: draft
created: 2026-07-15
tags: [bdd, showcase, melt, nav]
---

# bdd-09 — Dropdown Menu showcase component

> [!note] First `docs/bdds/` entry authored under this template's own construction
> `docs/bdds/` previously shipped only the `bdd-00` skeleton plus four
> project-authored entries (`bdd-04` … `bdd-08`); this is the fifth. It is the
> first Tier-2 slice of epic #178 (Melt-UI showcase build-out, task #15).

## Use case

As a **developer evaluating this template's component library** at
`/showcase/components/`, when I **open the Dropdown Menu demo's trigger
button**, I see a floating menu of actions — keyboard-navigable, one item
disabled, every label localized — matching the `nav/` row-actions /
user-menu shape the epic (#178) prioritizes this component for.

## Chosen build path (locked, [[MELT-UI]] / [[adr-08-frontend-and-design-system]] r8)

Melt 0.44 (pinned, [[REQUIREMENTS]]) ships no `Dropdown Menu` builder — the
epic comment's "36 builders" list names one, but it is not present in the
pinned version actually installed, and the Melt-first posture ([[MELT-UI]]
"posture") only reaches past a Melt builder when one genuinely isn't
available. This entry locks the ladder's next rung instead of a new builder
or a fully custom control:

- **Melt's `Popover` builder** (`melt/builders`, the same inline-instantiation
  pattern `DatePicker`/`DateRangePicker`/`Tooltip` already use — no shared
  `Popover` primitive exists yet, each consumer wires its own instance) is
  the float/anchor primitive: trigger, positioning, open/close state,
  outside-click and `Escape` dismissal.
- **shadcn-svelte's dropdown-menu interaction pattern** supplies the menu
  semantics Melt's `Popover` alone doesn't cover — roving `tabindex` focus
  across items, arrow-key cycling, typeahead-by-first-character, a disabled
  item that is skipped by both, and a separator convention — adapted onto
  the Melt popover's anchor/positioning plumbing rather than installed as a
  Bits UI dependency, since the float primitive stays Melt per the ladder.

This is a build-path decision the guardian sweep at PR close (`kdx-park`
task #15: "run `astro-drf-aws-adr` guardian … component/showcase/i18n/token
churn") re-verifies; it is not re-litigated in this entry.

## Scenarios

### Trigger opens the menu

```gherkin
Given the Dropdown Menu demo is rendered in the `nav/` section of
  `/showcase/components/`, closed, showing only its trigger button
When a user clicks (or activates via keyboard) the trigger
Then the menu opens as a floating panel anchored to the trigger, positioned
  and dismissed by the Melt `Popover` builder
And focus moves to the first enabled menu item
```

### Arrow-key navigation cycles through items

```gherkin
Given the menu is open with focus on one item
When the user presses `ArrowDown` or `ArrowUp`
Then focus moves to the next/previous item in the list, wrapping at either
  end
And a disabled item is included in the visual list but is skipped by arrow
  navigation — focus never lands on it
```

### Typeahead jumps to a matching item

```gherkin
Given the menu is open
When the user types a printable character
Then focus jumps to the next item (from the current position, wrapping)
  whose localized label starts with that character, case-insensitively
And repeating the same character cycles to the next match sharing that
  first character, matching shadcn-svelte's standard typeahead behavior
```

### Selecting an item fires its action and closes the menu

```gherkin
Given the menu is open with focus on an enabled item
When the user presses `Enter`/`Space`, or clicks the item
Then the item's associated demo action fires (client-side only — no
  network call, this is a showcase demo)
And the menu closes
And focus returns to the trigger button
```

### A disabled item is inert

```gherkin
Given the menu is open and showing at least one disabled item (the demo
  ships exactly one, styled with `--muted-foreground` / reduced opacity)
When the user clicks the disabled item, or tabs/arrows onto its position
Then no action fires and the menu does not close
And the disabled item carries `aria-disabled="true"` and is excluded from
  the roving-tabindex/typeahead sequence
```

### Escape dismisses without selecting

```gherkin
Given the menu is open
When the user presses `Escape`
Then the menu closes with no item's action firing
And focus returns to the trigger button — the Melt `Popover` builder's
  standard dismissal behavior, unchanged by the menu-semantics layer on top
```

### Every visible label is i18n-keyed

```gherkin
Given the trigger label, every menu item's label, and the demo's section
  heading in the gallery
When the page renders in any configured locale ([[LOCALISATION]])
Then each string is drawn from a `snake_case` English message ID
  (`demo_dropdown_*` / `gallery_dropdownmenu*`) via `t()` — no literal string
  is hardcoded in the component or the showcase page
```

### Tokenized surface, no canvas repaint

```gherkin
Given [[DESIGN-SYSTEM]]'s existing `--popover` / `--popover-foreground`
  surface token pair (already declared for exactly this kind of floating
  content) and its light/dark rule that a token without its `.dark` pair is
  a defect
When the Dropdown Menu's floating panel renders, in either mode
Then its background, text, border, and hover/focus states resolve only to
  existing CSS custom properties — no new literal colors, no new tokens
And the surrounding page canvas (`--canvas`, the melt dot-grid background)
  is untouched — the palette experiment from issue #178 is explicitly out
  of scope for this entry, deferred at the epic level
```

## Frontend half

New component `DropdownMenu.svelte` in `frontend/src/lib/components/nav/`
(category `nav/` per the epic's own Tier-2 table — "user menu, row
actions"), alongside the existing `Tabs.svelte`; exported from
`nav/index.ts`. It instantiates Melt's `Popover` builder directly (matching
the inline-instantiation pattern already used by `form/DatePicker.svelte`,
`form/DateRangePicker.svelte`, and `overlay/Tooltip.svelte` — no shared
`Popover` wrapper exists to reuse) and layers roving-focus, arrow-key,
typeahead, and disabled-item handling on top, per the build path above.

A showcase-only composition component, `DropdownMenuDemo.svelte`, is added
under `frontend/src/lib/components/showcase/` (alongside `TabsDemo.svelte`,
`TooltipDemo.svelte`) — realistic row-action sample data (e.g. Edit /
Duplicate / Archive *(disabled)* / Delete, echoing the epic's "row actions"
use case for a `DataTable` row) rather than the raw primitive, exactly the
existing `*Demo.svelte` convention. It is wired into
`frontend/src/pages/showcase/components.astro`'s `nav/` section next to
`TabsDemo`, `client:load`, all labels passed through `t()`.

`frontend/src/i18n/`'s catalog gains the `demo_dropdown_*` (trigger label,
item labels, disabled item label) and `gallery_dropdownmenu*` (section
heading, intro line) message IDs ([[LOCALISATION]]).

`docs/COMPONENTIZATION.md`'s Component index and folder-tree comment for
`nav/` gain the `DropdownMenu` / `DropdownMenuDemo` rows in the same PR
(task #15's "fold the melt 18-not-36 premise correction into this PR" note
also lands there, not in this entry — that is a documentation correction to
the epic's own comment, not a behavior this BDD governs).

## Backend half

None. This is a frontend-only showcase addition — no new `[[API]]` row, no
Django code, no migration. The [[adr-11-development-flow]] checkpoint
("does [[API]] solve the need?") resolves immediately: the existing
endpoint set already covers everything this feature touches, because it
touches none of them.

## Error handling

No network calls exist in this feature, so there is no server-error path.
The only failure mode is a degenerate demo state — if every item were
disabled, the menu would open with no reachable item — the shipped demo
data avoids this by construction (three enabled items, one disabled). Focus
management (trigger → first enabled item → back to trigger on close/select/
`Escape`) is the one behavior a regression could silently break; that is
what the shadow-test spec below exists to catch.

## Shadow-test spec

- `/showcase/components/` response body contains the `nav/DropdownMenu`
  demo's markers — trigger label and at least one item label — provable
  without a browser (`frontend/tests/smoke.test.ts`, same pattern already
  used for the `DataTable`/`Dialog`/`ThemeModeToggle` markers check).
- Real-browser flow, `kodex`-only, via the `chrome-devtools` MCP
  ([[AGENTS]]/[[DEVELOPMENT-LOOP]]'s smoke-test rule — never run headless
  or under the `pykodex` sandbox):
  1. Click the trigger → menu opens, focus on the first enabled item.
  2. `ArrowDown`/`ArrowUp` cycles focus across enabled items only, wrapping,
     skipping the disabled item.
  3. Typing a letter jumps focus to the next label starting with it.
  4. `Enter`/click on an enabled item fires its demo action and closes the
     menu, focus returns to the trigger.
  5. Click/activate on the disabled item does nothing, menu stays open.
  6. `Escape` closes the menu with no action fired, focus returns to the
     trigger.
  7. Visual check: the floating panel matches `--popover`/
     `--popover-foreground` in both light and dark mode, with no literal
     color and no canvas repaint.
- Until a project's shadow-test runner exists, this entry may reach
  `building`, never `shipped` — the same caveat [[bdd-06-profile-theming]]
  and [[bdd-07-melt-theme-sitewide]] already state.

## Parked during authoring

- [Issue #206](https://github.com/kodexArg/astro-drf-aws/issues/206) —
  `docs/GLOSSARY.md` has no row for individual Melt/shadcn showcase
  component names (none of the prior Tier-1 components have one either;
  they appear to be established through `docs/COMPONENTIZATION.md`'s index
  instead). Filed `draft`, unverified; this entry proceeds using "Dropdown
  Menu" / `DropdownMenu` as already locked with the owner in task #15 and
  issue #178, without adding a GLOSSARY row, consistent with precedent.
