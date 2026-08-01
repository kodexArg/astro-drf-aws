<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]] · [[MELT-UI]]
     LIVE-DOC:END -->

<!--
  The vendored Melt UI example ([[MELT-UI]] "Where this template uses it"):
  a fully custom control built with `melt/builders` — no shadcn-svelte/Bits
  UI equivalent ships this behavior (toggling `.dark` directly as part of
  its own state), per [[DESIGN-SYSTEM]]'s component-layering order.
-->
<script lang="ts">
  import { Toggle } from "melt/builders";
  import { Button } from "$lib/components/ui/button";
  import { Moon, Sun } from "$lib/components/icons";
  import { t } from "../../../i18n";
  import type { ThemeMode } from "$lib/theme";

  let {
    mode = $bindable<ThemeMode>("light"),
    disabled = false,
    /** Empty (default) keeps the icon-only square button; a truthy value (its
     * own text is no longer rendered) opts into the full-width icon+text row
     * (SessionBadge's popover), whose visible text is mode-derived — the mode
     * you switch TO, not the label string itself. */
    label = "",
  }: { mode?: ThemeMode; disabled?: boolean; label?: string } = $props();

  const toggle = new Toggle({
    value: () => mode === "dark",
    onValueChange: (isDark) => {
      mode = isDark ? "dark" : "light";
    },
    disabled: () => disabled,
  });
</script>

{#if label}
  <Button
    type="button"
    variant="bare"
    {...toggle.trigger}
    aria-label={t("theme_toggle_mode")}
    class="inline-flex h-9 w-full items-center justify-start gap-2 rounded-md border border-input bg-background px-3 text-sm font-medium shadow-sm hover:bg-accent hover:text-accent-foreground"
  >
    {#if toggle.value}
      <Moon class="size-4" aria-hidden="true" />
    {:else}
      <Sun class="size-4" aria-hidden="true" />
    {/if}
    <span>{toggle.value ? t("theme_to_light") : t("theme_to_dark")}</span>
  </Button>
{:else}
  <Button
    type="button"
    variant="bare"
    {...toggle.trigger}
    aria-label={t("theme_toggle_mode")}
    class="inline-flex size-9 items-center justify-center rounded-md border border-input bg-background text-sm font-medium shadow-sm hover:bg-accent hover:text-accent-foreground"
  >
    {#if toggle.value}
      <Moon class="size-4" aria-hidden="true" />
    {:else}
      <Sun class="size-4" aria-hidden="true" />
    {/if}
  </Button>
{/if}
