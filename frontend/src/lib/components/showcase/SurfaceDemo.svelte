<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Component-gallery demo of primitives/Surface (issue #130) — one tile per
  `level`, labeled with the level's own name so the six token-driven chrome
  presets are visually comparable side by side. Zero-props Surface (adr-22
  r1) is exercised implicitly: every instance below only ever sets `level`.
  Equal min-height frames keep the grid aligned; each Surface still carries
  its own level padding (page p-6 vs menu p-1, etc.).
-->
<script lang="ts">
  import Surface, { surfaceVariants, type SurfaceLevel } from "$lib/components/primitives/Surface.svelte";
  import { cn } from "$lib/utils";
  import { t } from "../../../i18n";

  const levels = Object.keys(surfaceVariants.level) as SurfaceLevel[];
</script>

<div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
  {#each levels as level (level)}
    <div class="flex min-w-0 flex-col gap-1.5">
      <span class="ml-1 text-xs font-medium leading-none text-muted-foreground">{level}</span>
      <div class="flex min-h-28 items-center justify-center">
        <Surface
          {level}
          class={cn(
            "text-center text-sm leading-snug",
            level === "pill" ? "inline-flex" : "flex w-full items-center justify-center",
          )}
        >
          {t("demo_surface_sample")}
        </Surface>
      </div>
    </div>
  {/each}
</div>
