<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]] · [[adr-28-nav-fsm-frosted-rail]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Site navigation: a two-mode drawer over NAV_SECTIONS, driven by
  shell/nav-fsm: preference (nav_lock cookie, SSR), presentation
  (rail|drawer), active (from Base.astro). Locked preference mounts rail +
  drawer together; CSS at RAIL_MIN_WIDTH picks which is visible so
  navigation never flashes unlocked ([[adr-28-nav-fsm-frosted-rail]]). No
  viewport measurement decides what renders. See [[bdd-12-navigation-shell]],
  [[COMPONENTIZATION]].
-->
<script lang="ts">
  import { onMount } from "svelte";
  import FancyDrawer from "$lib/components/overlay/FancyDrawer.svelte";
  import NavItem from "./NavItem.svelte";
  import NavLockToggle from "./NavLockToggle.svelte";
  import { NAV_SECTIONS, isActive } from "./nav";
  import {
    migrateLegacyNavLock,
    resolveNavFsm,
    writeNavLockCookie,
    type NavLockPreference,
  } from "./nav-fsm";
  import { ASIDE_SIZE_VAR, type AsideSize } from "./shell-sizes";
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

  let {
    pathname = "",
    side = "right",
    navigates = false,
    open = $bindable(false),
    /** SSR lock preference from the `nav_lock` cookie ([[adr-28-nav-fsm-frosted-rail]]). */
    preference: preferenceProp = "unlocked" as NavLockPreference,
    /**
     * Locked-rail / shell FancyDrawer width: L (15rem) | M (11rem, default) | S (9rem).
     * Tokens: `--shell-aside-*` in `app.css` ([[DESIGN-SYSTEM]] rem-over-px).
     */
    asideSize = "M" as AsideSize,
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
    asideSize?: AsideSize;
  } = $props();

  const railWidth = $derived(ASIDE_SIZE_VAR[asideSize]);
  const dense = $derived(asideSize === "S");

  let localPreference = $state<NavLockPreference | null>(null);
  let mode = $state<ThemeMode>(DEFAULTS.mode);

  const preference = $derived(localPreference ?? preferenceProp);
  const fsm = $derived(resolveNavFsm({ preference, active: pathname }));

  onMount(() => {
    mode = readThemeCookie().mode ?? DEFAULTS.mode;

    const migrated = migrateLegacyNavLock();
    if (migrated) localPreference = migrated;
  });

  function persistPreference(next: NavLockPreference) {
    localPreference = next;
    writeNavLockCookie(next);
    if (next === "locked") {
      open = false;
    }
  }

  function togglePin() {
    // CSS already forces the drawer below the rail floor (RAIL_MIN_WIDTH),
    // so a mobile guard here is not a behavior change ([[adr-28-nav-fsm-frosted-rail]] rule 2).
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
    class={cn(
      /* Gap after the last nav item before the divider + chrome (FancyDrawer
         is h-fit so mt-auto collapses to 0 — use a fixed margin). */
      "mt-6 flex shrink-0 items-center justify-center border-t border-border pt-4",
      dense ? "gap-1.5" : "gap-2.5",
    )}
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
    class={cn(
      "flex min-h-0 flex-1 flex-col overflow-y-auto",
      dense ? "gap-4" : "gap-6",
    )}
  >
    {#each NAV_SECTIONS as section, index (section.titleKey ?? index)}
      <div class={cn("flex flex-col", dense ? "gap-1.5" : "gap-2.5")}>
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
            {dense}
          />
        {/each}
      </div>
    {/each}
  </nav>
  {@render footer()}
{/snippet}

{#snippet rail()}
  <!-- Width reserve in the flex row; the visible rail is viewport-fixed so it
       stays screen-tall (h-dvh), not page-tall when <main> grows. -->
  <div
    class="shrink-0"
    style={`width: ${railWidth}`}
    aria-hidden="true"
    data-aside-spacer
  ></div>
  <aside
    class={cn(
      /* Viewport-fixed: inset-y-0 + h-dvh — not self-stretch to document height.
         pt-24 clears the content-column header range; pb-6 pins footer margin. */
      "fixed inset-y-0 z-30 flex h-dvh max-h-dvh flex-col overflow-y-auto pt-24 pb-6",
      dense ? "px-2" : "px-3",
      /* Soft wash + backdrop blur: a dotted theme background reads out of focus; labels stay sharp. */
      "bg-background/45 backdrop-blur-[0.35rem] supports-[backdrop-filter]:bg-background/35",
      /* Soft edge toward content via --border (no hard hairline); mirror when docked right. */
      isLeft
        ? "left-0 [box-shadow:0.0625rem_0_0.875rem_-0.25rem_color-mix(in_oklch,var(--border)_55%,transparent)]"
        : "right-0 [box-shadow:-0.0625rem_0_0.875rem_-0.25rem_color-mix(in_oklch,var(--border)_55%,transparent)]",
    )}
    data-aside-size={asideSize}
    style={`width: ${railWidth}`}
  >
    {@render body("inverse")}
  </aside>
{/snippet}

{#snippet drawer()}
  <FancyDrawer
    bind:open
    {side}
    width={railWidth}
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
