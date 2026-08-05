<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]] · [[adr-28-nav-fsm-frosted-rail]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Site navigation: a two-mode drawer over NAV_SECTIONS, driven by
  shell/nav-fsm: preference (nav_lock cookie, SSR), viewport band
  (matchMedia), presentation (rail|drawer), active (from Base.astro).
  Locked preference mounts rail + drawer together; CSS at RAIL_MIN_WIDTH
  picks which is visible so navigation never flashes unlocked
  ([[adr-28-nav-fsm-frosted-rail]]). See [[bdd-12-navigation-shell]],
  [[COMPONENTIZATION]].
-->
<script lang="ts">
  import { onMount } from "svelte";
  import FancyDrawer from "$lib/components/overlay/FancyDrawer.svelte";
  import NavItem from "./NavItem.svelte";
  import NavLockToggle from "./NavLockToggle.svelte";
  import { NAV_SECTIONS, isActive } from "./nav";
  import {
    DESK_MIN_WIDTH,
    RAIL_MIN_WIDTH,
    migrateLegacyNavLock,
    resolveNavFsm,
    resolvePresentation,
    resolveViewport,
    writeNavLockCookie,
    type NavLockPreference,
    type NavViewport,
  } from "./nav-fsm";
  import { t } from "../../../i18n";
  import {
    DEFAULTS,
    applyTheme,
    readThemeCookie,
    writeThemeCookie,
    type SidebarSide,
    type ThemeMode,
  } from "$lib/theme";
  import { Sun, Moon, User } from "$lib/components/icons";
  import { cn } from "$lib/utils";

  const RAIL_WIDTH = "14rem";

  let {
    pathname = "",
    side = "right",
    navigates = false,
    open = $bindable(false),
    /** SSR lock preference from the `nav_lock` cookie ([[adr-28-nav-fsm-frosted-rail]]). */
    preference: preferenceProp = "unlocked" as NavLockPreference,
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
    preference?: NavLockPreference;
  } = $props();

  let localPreference = $state<NavLockPreference | null>(null);
  let viewport = $state<NavViewport>("desk");
  let mode = $state<ThemeMode>(DEFAULTS.mode);

  const preference = $derived(localPreference ?? preferenceProp);
  const fsm = $derived(resolveNavFsm({ preference, viewport, active: pathname }));

  onMount(() => {
    mode = readThemeCookie().mode ?? DEFAULTS.mode;

    const migrated = migrateLegacyNavLock();
    if (migrated) localPreference = migrated;

    const railMq = window.matchMedia(`(min-width: ${RAIL_MIN_WIDTH})`);
    const deskMq = window.matchMedia(`(min-width: ${DESK_MIN_WIDTH})`);
    const syncViewport = () => {
      viewport = resolveViewport(railMq.matches, deskMq.matches);
    };
    syncViewport();
    railMq.addEventListener("change", syncViewport);
    deskMq.addEventListener("change", syncViewport);
    return () => {
      railMq.removeEventListener("change", syncViewport);
      deskMq.removeEventListener("change", syncViewport);
    };
  });

  function persistPreference(next: NavLockPreference) {
    localPreference = next;
    writeNavLockCookie(next);
    if (next === "locked" && resolvePresentation(next, viewport) === "rail") {
      open = false;
    }
  }

  function togglePin() {
    if (preference === "unlocked" && viewport === "mobile") return;
    persistPreference(preference === "locked" ? "unlocked" : "locked");
  }

  // See [[bdd-12-navigation-shell]].
  function toggleTheme() {
    const next: ThemeMode = mode === "dark" ? "light" : "dark";
    mode = next;
    const merged = { ...readThemeCookie(), mode: next };
    applyTheme(merged);
    writeThemeCookie(merged);
  }

  const themeIcon = $derived(mode === "dark" ? Moon : Sun);
  const isLeft = $derived(side === "left");
</script>

{#snippet footer()}
  <div
    class="mt-6 flex shrink-0 items-center justify-center gap-2.5 border-t border-border pt-4"
    role="group"
    aria-label={t("shell_nav_label")}
  >
    <NavLockToggle locked={fsm.presentation === "rail"} onclick={togglePin} />
    <a
      href={navigates ? "/profile/" : "#"}
      aria-label={t("shell_nav_profile")}
      title={t("shell_nav_profile")}
      class="inline-flex size-8 shrink-0 items-center justify-center rounded-full bg-foreground text-background transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
    >
      <User class="size-4" aria-hidden="true" />
    </a>
    <button
      type="button"
      aria-label={t("theme_toggle_mode")}
      title={t("theme_toggle_mode")}
      class="inline-flex size-8 shrink-0 items-center justify-center rounded-full bg-foreground text-background transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
      onclick={toggleTheme}
    >
      {#if themeIcon}
        {@const Icon = themeIcon}
        <Icon class="size-4" aria-hidden="true" />
      {/if}
    </button>
  </div>
{/snippet}

{#snippet body(tone: "default" | "inverse")}
  <nav
    aria-label={t("shell_nav_label")}
    class="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto"
  >
    {#each NAV_SECTIONS as section, index (section.titleKey ?? index)}
      <div class="flex flex-col gap-2.5">
        {#if section.titleKey}
          <div
            class="px-2 pb-1 text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-muted-foreground"
          >
            {t(section.titleKey)}
          </div>
        {/if}
        {#each section.items as item (item.href)}
          <NavItem
            href={navigates ? item.href : "#"}
            label={t(item.labelKey)}
            icon={item.icon}
            active={isActive(item.href, pathname)}
            {tone}
          />
        {/each}
      </div>
    {/each}
  </nav>
  {@render footer()}
{/snippet}

{#snippet rail()}
  <aside
    class={cn(
      "flex min-h-0 shrink-0 flex-col overflow-y-auto border-border px-3 py-4",
      /* Soft wash + backdrop blur: a dotted theme background reads out of focus; labels stay sharp. */
      "bg-background/45 backdrop-blur-[0.35rem] supports-[backdrop-filter]:bg-background/35",
      isLeft ? "border-r" : "order-last border-l",
    )}
    style={`width: ${RAIL_WIDTH}`}
  >
    {@render body("inverse")}
  </aside>
{/snippet}

{#snippet drawer()}
  <FancyDrawer
    bind:open
    {side}
    width={RAIL_WIDTH}
    title=""
    openLabel={t("shell_nav_label")}
    closeLabel={t("fancy_drawer_close")}
  >
    {@render body("default")}
  </FancyDrawer>
{/snippet}

{#if preference === "locked"}
  <!-- CSS picks rail vs drawer so SSR + navigation never flash unlocked. -->
  <div class="hidden min-[43.75rem]:contents">
    {@render rail()}
  </div>
  <div class="contents min-[43.75rem]:hidden">
    {@render drawer()}
  </div>
{:else}
  {@render drawer()}
{/if}
