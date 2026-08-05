/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
 * Governed by: [[adr-08-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

/**
 * The gallery's membership ledger.
 *
 * This does NOT drive rendering — `components.astro` and
 * `ShowcaseGalleryView.svelte` still hand-wire every slot: per-component
 * sample data and a per-component hydration decision genuinely cannot be
 * inferred from a path (see docs/COMPONENTIZATION.md's rung-1-vs-hydration
 * tension). What this file *is* the single source of truth for is the
 * coverage question: the gallery-coverage test reads it (together with that
 * test's own exclusions) to fail the moment a `.svelte` file lands under a
 * tracked category directory with neither a registry row nor a named,
 * justified exclusion.
 *
 * `path` is relative to `src/lib/components/`. `hydration` records the
 * `client:*` directive (or its absence) the component is actually given at
 * its call site — "none" means it renders inside an SSR body or is composed
 * by another island, with no hydration directive anywhere of its own.
 */
export type GalleryHydration = "none" | "load" | "visible" | "idle";

export interface GalleryRegistryEntry {
  path: string;
  category: string;
  hydration: GalleryHydration;
}

export const GALLERY_REGISTRY: GalleryRegistryEntry[] = [
  // ui/ — rendered directly inside ShowcaseGalleryView.svelte's SSR body.
  { path: "ui/button/button.svelte", category: "ui", hydration: "none" },
  { path: "ui/badge/badge.svelte", category: "ui", hydration: "none" },
  { path: "ui/alert/alert.svelte", category: "ui", hydration: "none" },
  { path: "ui/alert/alert-title.svelte", category: "ui", hydration: "none" },
  { path: "ui/alert/alert-description.svelte", category: "ui", hydration: "none" },
  { path: "ui/separator/separator.svelte", category: "ui", hydration: "none" },

  // primitives/ — SectionTitle repeats throughout the SSR body; PageCanvas
  // and PageTitle are the layout's, exhibited by every page rather than by a
  // gallery slot; Surface is exhibited via showcase/SurfaceDemo.
  { path: "primitives/titles/SectionTitle.svelte", category: "primitives", hydration: "none" },
  { path: "primitives/titles/PageTitle.svelte", category: "primitives", hydration: "none" },
  { path: "primitives/titles/PageHeading.svelte", category: "primitives", hydration: "none" },
  { path: "primitives/PageCanvas.svelte", category: "primitives", hydration: "none" },
  { path: "primitives/Surface.svelte", category: "primitives", hydration: "none" },

  // data/
  { path: "data/DataTable.svelte", category: "data", hydration: "load" },
  { path: "data/ChipFilterBar.svelte", category: "data", hydration: "load" },
  { path: "data/Pagination.svelte", category: "data", hydration: "load" },
  { path: "data/Collapsible.svelte", category: "data", hydration: "visible" },
  { path: "data/Tree.svelte", category: "data", hydration: "visible" },
  { path: "data/NumericValue.svelte", category: "data", hydration: "none" },
  { path: "data/StatusBadge.svelte", category: "data", hydration: "none" },

  // dashboard/
  { path: "dashboard/MetricTileStrip.svelte", category: "dashboard", hydration: "visible" },
  { path: "dashboard/MetricTile.svelte", category: "dashboard", hydration: "none" },
  { path: "dashboard/EntityGrid.svelte", category: "dashboard", hydration: "none" },
  { path: "dashboard/EntityCard.svelte", category: "dashboard", hydration: "none" },
  { path: "dashboard/SummaryCard.svelte", category: "dashboard", hydration: "none" },

  // form/ — every entry here escalates to client:visible: each is a real
  // Melt-backed control the user must actually interact with in the demo.
  { path: "form/Select.svelte", category: "form", hydration: "visible" },
  { path: "form/Combobox.svelte", category: "form", hydration: "visible" },
  { path: "form/Checkbox.svelte", category: "form", hydration: "visible" },
  { path: "form/Switch.svelte", category: "form", hydration: "visible" },
  { path: "form/DatePicker.svelte", category: "form", hydration: "visible" },
  { path: "form/DateRangePicker.svelte", category: "form", hydration: "visible" },
  { path: "form/PinInput.svelte", category: "form", hydration: "visible" },
  { path: "form/TagsInput.svelte", category: "form", hydration: "visible" },
  { path: "form/Calendar.svelte", category: "form", hydration: "visible" },
  { path: "form/RangeCalendar.svelte", category: "form", hydration: "visible" },
  { path: "form/Slider.svelte", category: "form", hydration: "visible" },
  { path: "form/ToggleGroup.svelte", category: "form", hydration: "visible" },

  // nav/
  { path: "nav/Tabs.svelte", category: "nav", hydration: "visible" },
  { path: "nav/DropdownMenu.svelte", category: "nav", hydration: "visible" },
  { path: "nav/ContextMenu.svelte", category: "nav", hydration: "visible" },
  { path: "nav/Menubar.svelte", category: "nav", hydration: "visible" },
  { path: "nav/TableOfContents.svelte", category: "nav", hydration: "visible" },

  // chat/ — ChatMessageList and ChatComposer are composed inside the ChatUI
  // island and carry no directive of their own.
  { path: "chat/ChatUI.svelte", category: "chat", hydration: "visible" },
  { path: "chat/ChatMessageList.svelte", category: "chat", hydration: "none" },
  { path: "chat/ChatComposer.svelte", category: "chat", hydration: "none" },

  // overlay/ — ConfirmDialog is composed inside ChatMessageList and the
  // auth flows, with no gallery trigger of its own.
  { path: "overlay/Dialog.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/Accordion.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/Tooltip.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/Popover.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/HoverCard.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/ScrollArea.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/Drawer.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/FancyDrawer.svelte", category: "overlay", hydration: "visible" },
  { path: "overlay/ConfirmDialog.svelte", category: "overlay", hydration: "none" },

  // feedback/
  { path: "feedback/Progress.svelte", category: "feedback", hydration: "visible" },
  { path: "feedback/Toast.svelte", category: "feedback", hydration: "idle" },

  // auth/ — SessionBadge and ProfileForm hydrate at their real call sites
  // (Base.astro's header, profile.astro), both client:load.
  { path: "auth/AuthPanel.svelte", category: "auth", hydration: "visible" },
  { path: "auth/SessionBadge.svelte", category: "auth", hydration: "load" },
  { path: "auth/ProfileForm.svelte", category: "auth", hydration: "load" },

  // theme/ — QuickThemeToggle is composed inside SessionBadge's popover.
  { path: "theme/ThemeModeToggle.svelte", category: "theme", hydration: "visible" },
  { path: "theme/QuickThemeToggle.svelte", category: "theme", hydration: "none" },
  { path: "theme/ThemeCard.svelte", category: "theme", hydration: "load" },
  { path: "theme/PaletteFields.svelte", category: "theme", hydration: "none" },

  // shell/ — the site's navigation chrome. NavItem/NavBadge/NavbarIcon are
  // exhibited inert in the gallery's SSR body (adr-22 rule 2); NavDrawer is
  // the one shell member that holds open/closed state, so the gallery
  // hydrates it; ChatDrawer lives only in Base.astro (client:load).
  { path: "shell/NavItem.svelte", category: "shell", hydration: "none" },
  { path: "shell/NavBadge.svelte", category: "shell", hydration: "none" },
  { path: "shell/NavbarIcon.svelte", category: "shell", hydration: "none" },
  { path: "shell/NavLockToggle.svelte", category: "shell", hydration: "none" },
  { path: "shell/NavDrawer.svelte", category: "shell", hydration: "visible" },
  { path: "shell/ChatDrawer.svelte", category: "shell", hydration: "load" },

  // showcase/ — the demo wrappers themselves; each records the directive its
  // own mount carries in components.astro (SurfaceDemo is pure SSR).
  { path: "showcase/PaginationDemo.svelte", category: "showcase", hydration: "load" },
  { path: "showcase/CollapsibleDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/TreeDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/PinInputDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/TagsInputDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/CalendarDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/RangeCalendarDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/SliderDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/ToggleGroupDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/TabsDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/DropdownMenuDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/ContextMenuDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/MenubarDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/TableOfContentsDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/TooltipDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/PopoverDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/HoverCardDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/ScrollAreaDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/DrawerDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/ToastTriggerDemo.svelte", category: "showcase", hydration: "visible" },
  { path: "showcase/SurfaceDemo.svelte", category: "showcase", hydration: "none" },
];
