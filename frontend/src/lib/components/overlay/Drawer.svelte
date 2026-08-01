<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<script lang="ts">
  import { cn } from "$lib/utils";
  import { ChevronLeft, ChevronRight } from "$lib/components/icons";
  import { t } from "../../../i18n";
  import type { Snippet } from "svelte";

  let {
    open = $bindable(false),
    side = "left",
    title = "",
    width = "18rem",
    openLabel = t("drawer_open"),
    closeLabel = t("drawer_close"),
    children,
    class: className = undefined,
  }: {
    open?: boolean;
    side?: "left" | "right";
    title?: string;
    width?: string;
    openLabel?: string;
    closeLabel?: string;
    children?: Snippet;
    class?: string;
  } = $props();

  const isLeft = $derived(side === "left");
  const offClass = $derived(isLeft ? "-translate-x-full" : "translate-x-full");
  const Glyph = $derived(
    isLeft ? (open ? ChevronLeft : ChevronRight) : open ? ChevronRight : ChevronLeft,
  );
</script>

<aside
  class={cn(
    "fixed inset-y-0 z-40 flex transition-transform duration-base ease-out motion-reduce:transition-none",
    isLeft ? "left-0" : "right-0",
    !open && offClass,
    className,
  )}
  style={`width: ${width}`}
>
  <div
    inert={!open}
    aria-hidden={!open}
    class={cn(
      "flex min-w-0 flex-1 flex-col gap-4 overflow-y-auto bg-background p-4 shadow-xl",
      isLeft ? "border-r border-border" : "border-l border-border",
    )}
  >
    {#if title}
      <h2 class="truncate text-sm font-semibold text-foreground">{title}</h2>
    {/if}

    {#if children}
      {@render children()}
    {:else}
      <p class="text-sm text-muted-foreground">{t("drawer_empty")}</p>
    {/if}
  </div>

  <button
    type="button"
    onclick={() => (open = !open)}
    aria-label={open ? closeLabel : openLabel}
    aria-expanded={open}
    class={cn(
      "absolute top-1/2 flex h-14 w-8 -translate-y-1/2 cursor-pointer items-center justify-center border border-border bg-background text-muted-foreground shadow-md transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
      isLeft ? "left-full rounded-r-lg border-l-0" : "right-full rounded-l-lg border-r-0",
    )}
  >
    <Glyph class="size-4" aria-hidden="true" />
  </button>
</aside>
