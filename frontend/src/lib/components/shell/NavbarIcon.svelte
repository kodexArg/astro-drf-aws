<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!-- Shared chrome for every navbar icon control; consumers own the glyph and
     the behaviour ([[DESIGN-SYSTEM]]). -->
<script lang="ts">
  import type { Component } from "svelte";
  import { cn } from "$lib/utils";
  import { t } from "../../../i18n";

  let {
    icon = undefined,
    label = "",
    active = false,
    onclick = undefined,
    class: className = undefined,
    ...rest
  }: {
    /** Omitted renders the placeholder dot, so a bare mount still shows a
     * real control ([[adr-23-showcase-ready-components]] r1). */
    icon?: Component<{ class?: string; "aria-hidden"?: string }>;
    /** Accessible name; Spanish, resolved by the caller ([[LOCALIZATION]]). */
    label?: string;
    active?: boolean;
    /** No-op by default ([[adr-23-showcase-ready-components]] r2). */
    onclick?: () => void;
    class?: string;
    [key: string]: unknown;
  } = $props();

  const Glyph = $derived(icon);
  const accessibleName = $derived(label || t("navbar_icon_fallback"));
</script>

<button
  type="button"
  aria-label={accessibleName}
  aria-pressed={active}
  onclick={() => onclick?.()}
  class={cn(
    "inline-flex size-9 items-center justify-center rounded-full transition-colors",
    "hover:bg-accent",
    "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
    // Tailwind emits hover variants after base utilities, so a bare
    // `hover:text-*` here would outrank the active token ([[DESIGN-SYSTEM]]).
    active
      ? "text-accent-active hover:text-accent-active"
      : "text-foreground hover:text-accent-foreground",
    className,
  )}
  {...rest}
>
  {#if Glyph}
    <Glyph class="size-5" aria-hidden="true" />
  {:else}
    <span aria-hidden="true" class="size-2 rounded-full bg-current"></span>
  {/if}
</button>
