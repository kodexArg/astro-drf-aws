<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  The site's navigation: the NAV_ITEMS routes as buttons, behind a tab at the
  viewport edge, hidden until asked for.

  Composition, not a new widget. The panel is `overlay/Drawer.svelte` — the same
  component the showcase gallery exhibits — and each link is
  `shell/NavItem.svelte`. Nothing is forked for the app's use, which is what
  [[COMPONENTIZATION]] means by a gallery component being reused as-is.

  The list is NAV_ITEMS and nothing else. It is already the single registry of
  routes with their labels and icons; a second list here would be a second
  authority that can disagree with it.

  Rung 3 of the ladder ([[adr-04-frontend-and-design-system]] rule 3), and only
  just: the drawer holds open/closed state, which rung 1 cannot and rung 2 would
  need a round-trip for. The links are plain anchors, but real navigation is
  caller-enabled via `navigates` — inert by default (adr-22 rule 2).
-->
<script lang="ts">
  import Drawer from "$lib/components/overlay/Drawer.svelte";
  import NavItem from "./NavItem.svelte";
  import { NAV_ITEMS, isActive } from "./nav";
  import { t } from "../../../i18n";
  import type { SidebarSide } from "$lib/theme";

  let {
    pathname = "",
    side = "right",
    navigates = false,
    open = $bindable(false),
  }: {
    /**
     * The current path, supplied by the page. Read from a prop rather than from
     * `window` so the drawer renders identically on the server — a client-only
     * active state would flash the wrong item on first paint.
     */
    pathname?: string;
    /** Dock edge from `sidebarSide` (theme); ChatDrawer takes the mirror. */
    side?: SidebarSide;
    /** Enables the links' real hrefs; defaults to inert (adr-22 rule 2). */
    navigates?: boolean;
    open?: boolean;
  } = $props();
</script>

<Drawer
  bind:open
  {side}
  width="17rem"
  title={t("shell_nav_label")}
  openLabel={t("shell_nav_label")}
  closeLabel={t("drawer_close")}
>
  <nav aria-label={t("shell_nav_label")} class="flex flex-col gap-1">
    {#each NAV_ITEMS as item (item.href)}
      <NavItem
        href={navigates ? item.href : "#"}
        label={t(item.labelKey)}
        icon={item.icon}
        active={isActive(item.href, pathname)}
      />
    {/each}
  </nav>
</Drawer>
