<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Content, not a landmark: the `<main>` is the layout's, supplied once by
  `PageCanvas` — and with it the no-background rule this file used to state
  for itself, which mattered most here, on the exact page that controls the
  canvas.
-->
<script lang="ts">
  import type { Snippet } from "svelte";

  let { title, intro, children }: { title: string; intro: string; children?: Snippet } =
    $props();
</script>

<div class="flex w-full flex-1 flex-col items-center gap-8 px-6 py-16">
  <div class="flex flex-col items-center gap-2 text-center">
    <p class="text-muted-foreground">{intro}</p>
  </div>
  <!-- Profile fields first (narrow); appearance below uses the full content
       width so dual palettes / packs are not squeezed into a side column. -->
  <div class="flex w-full max-w-5xl flex-col items-stretch gap-8">
    {@render children?.()}
  </div>
</div>
