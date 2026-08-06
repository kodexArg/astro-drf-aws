<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  The page's one `<main>` landmark, supplied by the layout ([[GLOSSARY]]: Page
  Canvas). Two things it deliberately does NOT do:

  No background. `body` paints the canvas with `background-attachment: fixed`
  (the dots must not move on scroll); an opaque `<main>` would occlude it.
  That is the same reasoning ChatView and ProfileView each carried before
  this component existed to hold it once.

  No measure. Gutters and max-width belong to the page body, not to the
  landmark — a data-dense table and a settings column want different ones,
  and deciding here would force one on both.

  No header clearance: the header is in-flow (sticky), so it already reserves
  its own space — a second reservation here would double it.

  `flex-1`, not `min-h-dvh`: `body` → `.app-shell` (row) → locked rail +
  content column (header + this `<main>`); this fills what the header leaves
  in that column. A full-viewport min-height here would start below the
  header and end a header-height past the fold — the phantom scroll that
  pushed the standalone chat's composer off-screen. Long pages still stretch
  `body` past one viewport as before.
-->

<script lang="ts">
  import type { Snippet } from "svelte";

  let { children }: { children?: Snippet } = $props();
</script>

<main class="flex min-w-0 w-full flex-1 flex-col p-12 pb-4 pt-16">
  {@render children?.()}
</main>
