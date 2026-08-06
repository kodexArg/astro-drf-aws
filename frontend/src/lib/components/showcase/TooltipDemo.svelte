<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]]
     LIVE-DOC:END -->

<!--
  Component-gallery demo of overlay/Tooltip — Tooltip's `trigger` prop is a
  parameterized Snippet<[Tooltip]>, which Astro's slot mechanism cannot pass
  through, so the #snippet lives here (same reason showcase/AlertDialogDemo.svelte
  exists) and this composition is dropped into the gallery page as a single
  client:load island.

  Spread `{...t.trigger}` onto a native <button>, not ui/Button: Melt's
  attachment symbols + pointer handlers must land on the real element
  (same pattern as primitives/titles/PageHeading.svelte).
-->
<script lang="ts">
  import { Tooltip } from "$lib/components/overlay";

  let {
    triggerLabel,
    content,
  }: {
    triggerLabel: string;
    content: string;
  } = $props();
</script>

<Tooltip {content}>
  {#snippet trigger(t)}
    <button
      type="button"
      {...t.trigger}
      class="inline-flex h-9 w-fit items-center justify-center gap-2 whitespace-nowrap rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
    >
      {triggerLabel}
    </button>
  {/snippet}
</Tooltip>
