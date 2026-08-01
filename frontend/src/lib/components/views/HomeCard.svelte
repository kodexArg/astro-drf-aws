<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  One row of the home's single-column card list — an icon, a title, and a
  short, non-invasive abstract, wrapped in a single navigating `<a>`.
  Purely presentational: the icon and copy already arrive localized/resolved
  from the caller (HomeCardsView), so this component imports no i18n and
  performs no navigation side effect beyond the plain link itself
  (adr-22 rule 2). `icon` is a Lucide component from the `icons/` registry
  ([[FRONTEND]]) — never a hand-fabricated SVG or emoji glyph; a zero-prop
  mount omits it entirely and never throws (adr-22 rule 1).
-->
<script lang="ts">
  import * as Card from "$lib/components/ui/card";
  import type { Component } from "svelte";

  let {
    href = "#",
    icon = undefined,
    title = "",
    abstract = "",
  }: {
    href?: string;
    /** Lucide icon component from `$lib/components/icons`, rendered `aria-hidden`. */
    icon?: Component<{ class?: string; "aria-hidden"?: string }>;
    title?: string;
    abstract?: string;
  } = $props();
</script>

<a {href} class="block focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
  <Card.Root class="border-border/40 shadow-sm transition-colors hover:bg-muted">
    <Card.Content class="flex items-center gap-4">
      {#if icon}
        {@const Icon = icon}
        <Icon class="size-6 shrink-0" aria-hidden="true" />
      {/if}
      <div class="flex flex-col gap-0.5">
        <span class="font-medium">{title}</span>
        <span class="text-sm text-muted-foreground">{abstract}</span>
      </div>
    </Card.Content>
  </Card.Root>
</a>
