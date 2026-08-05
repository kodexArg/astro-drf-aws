<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<script lang="ts">
  import SectionTitle from "./SectionTitle.svelte";
  import Tooltip from "$lib/components/overlay/Tooltip.svelte";
  import { Info } from "$lib/components/icons";

  let {
    title = "",
    help = "",
    helpLabel = "",
  }: {
    title?: string;
    help?: string;
    helpLabel?: string;
  } = $props();
</script>

<div class="flex items-center gap-2">
  <SectionTitle as="h1">{title}</SectionTitle>

  {#if help}
    <Tooltip content={help} side="bottom">
      {#snippet trigger(tooltip)}
        <button
          type="button"
          {...tooltip.trigger}
          aria-label={helpLabel}
          class="inline-flex size-6 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        >
          <Info class="size-4" aria-hidden="true" />
        </button>
      {/snippet}
    </Tooltip>
  {/if}
</div>
