<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]]
     LIVE-DOC:END -->

<!--
  Single-date filter on the melt/builders Popover ([[MELT-UI]]) — Melt 0.44
  ships no Date Picker builder, so the month grid is form/Calendar (hand-
  rolled for the same absence) and Popover supplies the anchored, focus-
  trapped surface around it. Value is a plain ISO "YYYY-MM-DD" string — no
  @internationalized/date dependency.
-->
<script lang="ts">
  import { Popover } from "melt/builders";
  import { Button } from "$lib/components/ui/button";
  import Calendar from "./Calendar.svelte";
  import { cn } from "$lib/utils";

  let {
    value = $bindable(undefined),
    label,
    placeholder = "",
    clearLabel = "",
    min = undefined,
    max = undefined,
    class: className = undefined,
  }: {
    value?: string | undefined;
    /** Accessible label, i18n-supplied by the caller. */
    label: string;
    placeholder?: string;
    /** Shown next to a chosen value; omit to hide the clear affordance. */
    clearLabel?: string;
    min?: string;
    max?: string;
    class?: string;
  } = $props();

  const popover = new Popover();

  const formatted = $derived(
    value
      ? new Date(`${value}T00:00:00`).toLocaleDateString(undefined, { dateStyle: "medium" })
      : undefined,
  );

  function onSelect(_iso: string): void {
    popover.open = false;
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
    <Calendar bind:value {min} {max} class="border-0" onValueChange={onSelect} />
    {#if value && clearLabel}
      <div class="border-t border-border px-2 pb-2 pt-1">
        <Button type="button" variant="ghost" size="sm" onclick={() => (value = undefined)}>
          {clearLabel}
        </Button>
      </div>
    {/if}
  </div>
</div>
