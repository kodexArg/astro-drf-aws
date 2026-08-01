<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Quick toggle housed in SessionBadge's ☰ menu (docs/bdds/bdd-07-melt-theme-sitewide.md).
  The theme_config blob is authoritative and the cookie is a render cache, so the
  caller supplies persistence via `onPersist`; an anonymous mount stays
  cookie-only since there is no DB row to persist to. Wraps ThemeModeToggle
  ([[MELT-UI]]) with zero edits to it — every other themed key (bgPreset,
  colors, radius) is untouched here.
-->
<script lang="ts">
  import ThemeModeToggle from "$lib/components/theme/ThemeModeToggle.svelte";
  import {
    DEFAULTS,
    readThemeCookie,
    applyTheme,
    writeThemeCookie,
    type ThemeConfig,
    type ThemeMode,
  } from "$lib/theme";

  let {
    label = "",
    onPersist,
  }: { label?: string; onPersist?: (blob: ThemeConfig) => void } = $props();

  let mode = $state<ThemeMode>(readThemeCookie().mode ?? DEFAULTS.mode);

  function setMode(next: ThemeMode): void {
    mode = next;
    const merged = { ...readThemeCookie(), mode: next };
    applyTheme(merged);
    writeThemeCookie(merged);
    onPersist?.(merged);
  }
</script>

<ThemeModeToggle bind:mode={() => mode, setMode} {label} />
