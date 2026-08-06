<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]]
     LIVE-DOC:END -->

<!--
  From/to date-range filter on the melt/builders Popover ([[MELT-UI]]) — same
  composition as form/DatePicker: form/RangeCalendar supplies the month grid
  (Melt 0.44 has no RangeCalendar builder), Popover supplies the anchored,
  focus-trapped surface. Two independently bindable ISO "YYYY-MM-DD" strings.
-->
<script lang="ts">
  import { Popover } from "melt/builders";
  import { Button } from "$lib/components/ui/button";
  import RangeCalendar from "./RangeCalendar.svelte";
  import { cn } from "$lib/utils";

  let {
    from = $bindable(undefined),
    to = $bindable(undefined),
    label,
    fromLabel: _fromLabel,
    toLabel: _toLabel,
    placeholder = "",
    clearLabel = "",
    min = undefined,
    max = undefined,
    class: className = undefined,
  }: {
    from?: string | undefined;
    to?: string | undefined;
    /** Accessible label for the trigger, i18n-supplied by the caller. */
    label: string;
    /** Kept for API stability with the prior native dual-input surface. */
    fromLabel: string;
    /** Kept for API stability with the prior native dual-input surface. */
    toLabel: string;
    placeholder?: string;
    /** Shown next to a chosen range; omit to hide the clear affordance. */
    clearLabel?: string;
    min?: string;
    max?: string;
    class?: string;
  } = $props();

  const popover = new Popover();

  const format = (iso: string) =>
    new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { dateStyle: "medium" });
  const formatted = $derived(
    from && to ? `${format(from)} – ${format(to)}` : from ? format(from) : to ? format(to) : undefined,
  );

  function onRangeChange(range: { from?: string; to?: string }): void {
    if (range.from && range.to) popover.open = false;
  }
</script>

<div class={cn("flex flex-col gap-1.5", className)}>
  <Button
    type="button"
    variant="outline"
    {...popover.trigger}
    aria-label={label}
    class="w-full justify-between font-normal"
  >
    <span class={cn("truncate", !formatted && "text-muted-foreground")}>
      {formatted ?? placeholder}
    </span>
    <span aria-hidden="true" class={cn("shrink-0 transition-transform", popover.open && "rotate-180")}>⌄</span>
  </Button>
  <div
    {...popover.content}
    class="z-50 rounded-md border bg-popover p-0 text-popover-foreground shadow-md"
  >
    <RangeCalendar bind:from bind:to {min} {max} class="border-0" {onRangeChange} />
    {#if (from || to) && clearLabel}
      <div class="border-t border-border px-2 pb-2 pt-1">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onclick={() => {
            from = undefined;
            to = undefined;
          }}
        >
          {clearLabel}
        </Button>
      </div>
    {/if}
  </div>
</div>
