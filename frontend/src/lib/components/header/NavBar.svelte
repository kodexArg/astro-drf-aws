<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  let {
    title = "",
    class: className = undefined,
    actions,
  }: {
    title?: string;
    class?: string;
    actions?: Snippet;
  } = $props();
</script>

<div
  class={cn(
    "nav-pill sunken relative flex w-full items-center justify-between gap-4 rounded-full py-1.5 pl-5 pr-1.5 text-foreground",
    className,
  )}
>
  <h1 class="truncate font-display text-2xl font-bold tracking-tight text-primary">{title}</h1>
  <div class="flex shrink-0 items-center gap-2">{@render actions?.()}</div>
</div>
