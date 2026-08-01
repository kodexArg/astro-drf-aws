<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Component-gallery demo of primitives/Surface (issue #130) — one tile per
  `level`, labeled with the level's own name so the six token-driven chrome
  presets are visually comparable side by side. Zero-props Surface (adr-22
  r1) is exercised implicitly: every instance below only ever sets `level`.
-->
<script lang="ts">
  import Surface, { surfaceVariants, type SurfaceLevel } from "$lib/components/primitives/Surface.svelte";
  import { t } from "../../../i18n";

  const levels = Object.keys(surfaceVariants.level) as SurfaceLevel[];
</script>

<div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
  {#each levels as level (level)}
    <div class="flex flex-col gap-2">
      <span class="text-xs font-medium text-muted-foreground">{level}</span>
      <Surface {level}>{t("demo_surface_sample")}</Surface>
    </div>
  {/each}
</div>
