<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Content, not a landmark: the `<main>` is the layout's, supplied once by
  `PageCanvas` — and with it the no-background rule this file used to state
  for itself.

  `flex-1` rather than `min-h-screen`: the height to fill is what PageCanvas
  has left after the header, not a second full viewport. The slotted ChatUI
  island fills it.
-->
<script lang="ts">
  import type { Snippet } from "svelte";

  let { children }: { children?: Snippet } = $props();
</script>

<div class="relative flex w-full flex-1">
  {@render children?.()}
</div>
