<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Pin control for NavDrawer's footer: locked = docked rail, unlocked =
  floating FancyDrawer. Icon-only disc, zero-prop safe (adr-23 rule 1); the
  click callback defaults to undefined so a bare mount performs no action
  (adr-23 rule 2).
-->
<script lang="ts">
  import { cn } from "$lib/utils";
  import { Lock, LockOpen } from "$lib/components/icons";
  import { t } from "../../../i18n";

  let {
    locked = false,
    class: className = undefined,
    onclick,
  }: {
    locked?: boolean;
    class?: string;
    onclick?: (event: MouseEvent) => void;
  } = $props();

  const aria = $derived(locked ? t("shell_nav_unlock_aria") : t("shell_nav_lock_aria"));
  const Glyph = $derived(locked ? Lock : LockOpen);
</script>

<button
  type="button"
  {onclick}
  aria-pressed={locked}
  aria-label={aria}
  title={aria}
  class={cn(
    "inline-flex size-8 shrink-0 items-center justify-center rounded-full bg-foreground text-background transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
    className,
  )}
>
  <Glyph class="size-4" aria-hidden="true" />
</button>
