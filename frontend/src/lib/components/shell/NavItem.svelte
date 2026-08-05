<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

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
    class: className = undefined,
    ...rest
  }: {
    href?: string;
    label?: string;
    active?: boolean;
    count?: number;
    icon?: Component<{ class?: string; "aria-hidden"?: string }>;
    tone?: "default" | "inverse";
    class?: string;
    [key: string]: unknown;
  } = $props();

  const Icon = $derived(icon);
  const inverse = $derived(tone === "inverse");
</script>

<Button
  {href}
  variant={active ? "secondary" : inverse ? "bare" : "ghost"}
  class={cn(
    "w-full justify-start gap-3 text-base",
    inverse && !active && "text-foreground/90 hover:bg-foreground/10",
    className,
  )}
  aria-current={active ? "page" : undefined}
  {...rest}
>
  {#if Icon}
    <Icon class="size-5 shrink-0" aria-hidden="true" />
  {/if}
  <span class="truncate">{label}</span>
  <NavBadge {count} />
</Button>
