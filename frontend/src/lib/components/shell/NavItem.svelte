<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Nav capsule: circular icon disc is the left cap; active/hover fill
  projects right as a pill (feedlot NavItem pattern, token-adapted).
-->
<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { cn } from "$lib/utils";
  import NavBadge from "./NavBadge.svelte";
  import type { Component } from "svelte";

  let {
    href = "#",
    label = "",
    active = false,
    count = 0,
    icon = undefined,
    /** `inverse` drops the ghost hover fill for a rail sitting directly on
     * the canvas with no panel behind it (docked/pinned NavDrawer). */
    tone = "default",
    /** Tighter gap/padding for asideSize S (icon + short label). */
    dense = false,
    class: className = undefined,
    ...rest
  }: {
    href?: string;
    label?: string;
    active?: boolean;
    count?: number;
    icon?: Component<{ class?: string; "aria-hidden"?: string }>;
    tone?: "default" | "inverse";
    dense?: boolean;
    class?: string;
    [key: string]: unknown;
  } = $props();

  const Icon = $derived(icon);
  const inverse = $derived(tone === "inverse");
</script>

<Button
  {href}
  variant="bare"
  class={cn(
    "group flex h-8 w-full items-center rounded-full py-0 pl-0 text-left text-sm font-medium leading-tight transition-colors",
    dense ? "gap-1.5 pr-2" : "gap-2 pr-3",
    "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
    inverse
      ? active
        ? "bg-foreground/15 text-foreground"
        : "text-foreground/90 hover:bg-foreground/10"
      : active
        ? "bg-accent/45 text-foreground"
        : "text-foreground hover:bg-accent/30",
    className,
  )}
  aria-current={active ? "page" : undefined}
  {...rest}
>
  {#if Icon}
    <span
      class={cn(
        "grid size-8 shrink-0 place-items-center rounded-full border transition-colors",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : inverse
            ? "border-border bg-foreground/5 text-foreground/80 group-hover:bg-foreground/10 group-hover:text-foreground"
            : "border-border bg-muted text-muted-foreground group-hover:bg-background group-hover:text-foreground",
      )}
      aria-hidden="true"
    >
      <Icon class="size-3.5" aria-hidden="true" />
    </span>
  {/if}
  <span class="min-w-0 flex-1 truncate">{label}</span>
  <NavBadge {count} />
</Button>
