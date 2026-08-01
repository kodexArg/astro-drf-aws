<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  The named surface primitive between the token set (DESIGN-SYSTEM.md) and
  finished components (issue #130). It owns only the chrome — border, radius,
  background/foreground pair, padding, shadow — of a raised or contained
  region; layout classes (flex, gap, etc.) are the caller's concern, passed
  through `class`.
-->
<script lang="ts" module>
  export const surfaceVariants = {
    level: {
      page: "rounded-xl border bg-card text-card-foreground shadow",
      tile: "rounded-lg border bg-card text-card-foreground px-4 py-3",
      floating: "rounded-md border bg-popover text-popover-foreground p-4 shadow-md",
      menu: "rounded-md border bg-popover text-popover-foreground p-1 shadow-md",
      control: "rounded-md border border-input bg-background px-3 py-2",
      pill: "rounded-full px-3 py-1",
    },
  } as const;

  export type SurfaceLevel = keyof typeof surfaceVariants.level;
</script>

<script lang="ts">
  import { cn } from "$lib/utils";

  let {
    class: className = undefined,
    level = "tile",
    children,
    ...rest
  }: {
    class?: string;
    level?: SurfaceLevel;
    children?: import("svelte").Snippet;
    [key: string]: unknown;
  } = $props();

  const classes = $derived(cn(surfaceVariants.level[level], className));
</script>

<div class={classes} {...rest}>
  {@render children?.()}
</div>
