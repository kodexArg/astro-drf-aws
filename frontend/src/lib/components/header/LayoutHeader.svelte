<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<script lang="ts">
  import NavBar from "./NavBar.svelte";
  import type { Snippet } from "svelte";

  let {
    title = "",
    session,
  }: {
    title?: string;
    session?: Snippet;
  } = $props();
</script>

<!-- The 2rem travel gap lives here, not on the header: sticky top-0 with an
     internal offset would pin the pill below the viewport top forever
     (issue #287). This sentinel is also the IntersectionObserver target
     Base.astro uses to toggle the docked state. -->
<div data-nav-sentinel class="h-8 w-full" aria-hidden="true"></div>
<header data-nav-header class="sticky top-0 z-20 w-full px-6 sm:px-10">
  <NavBar {title} actions={session} />
</header>
