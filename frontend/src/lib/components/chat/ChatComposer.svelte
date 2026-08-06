<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]] · [[adr-17-chatbot-two-tier]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]] · [[CHATBOT]]
     LIVE-DOC:END -->

<!--
  The composer only collects the user's raw utterance and hands it up via
  `onsubmit` ([[CHATBOT]]). It never renders assistant text and holds no
  actuator rights — the two-tier split (adr-15) lives above it in ChatUI.
-->
<script lang="ts">
  import { onDestroy, untrack } from "svelte";
  import { Button } from "$lib/components/ui/button";
  import { Send } from "$lib/components/icons";
  import { cn } from "$lib/utils";
  import { createTypewriterCycle, type Scheduler } from "$lib/typewriter-placeholder";

  let {
    pending = false,
    placeholder = "Type a message",
    ariaLabel,
    sendLabel,
    placeholderExamples = [],
    onsubmit,
    class: className = undefined,
  }: {
    pending?: boolean;
    /** Rendered copy arrives resolved from the page's frontmatter (LOCALIZATION) */
    placeholder?: string;
    ariaLabel: string;
    sendLabel: string;
    /** Typewriter phrases to cycle; empty disables the cycle. */
    placeholderExamples?: string[];
    onsubmit: (text: string) => void;
    class?: string;
  } = $props();

  const uid = $props.id();

  /**
   * Padding-driven resting height (px): 1+1 border + 8+8 py-2 + 20 leading-5.
   * Textareas top-align — height follows pad + line, not a locked button height.
   */
  const RESTING_H_PX = 38;

  let value = $state("");
  let animatedPlaceholder = $state("");
  let textareaEl: HTMLTextAreaElement | undefined = $state();
  /** True when autosize raised the field above resting height (button pins to bottom). */
  let tall = $state(false);

  const realScheduler: Scheduler = {
    set: (cb, ms) => setTimeout(cb, ms),
    clear: (handle) => clearTimeout(handle as ReturnType<typeof setTimeout>),
  };

  // Phrases are fixed for the cycle lifetime; untrack documents the intentional init capture.
  const cycle = createTypewriterCycle(
    untrack(() => placeholderExamples),
    { typeMs: 45, holdMs: 10000, deleteMs: 25 },
    realScheduler,
  );
  cycle.onUpdate((text) => {
    animatedPlaceholder = text;
  });

  $effect(() => {
    if (value.length === 0 && placeholderExamples.length > 0) {
      cycle.start();
    } else {
      cycle.stop();
    }
  });

  onDestroy(() => cycle.stop());

  /**
   * Pin resting height in px so UA/rows cannot inflate a single line.
   * Growth only when scrollHeight (+ borders) exceeds RESTING_H_PX.
   * Measure from height:0 so padding + line-height alone decide need.
   */
  function autoresize(): void {
    const el = textareaEl;
    if (!el) return;
    if (!el.value) {
      el.style.height = `${RESTING_H_PX}px`;
      tall = false;
      return;
    }
    // Collapse first — `height:auto` keeps UA/rows min and over-reports.
    el.style.height = "0px";
    const style = getComputedStyle(el);
    const borderY =
      parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
    const needed = el.scrollHeight + borderY;
    if (needed > RESTING_H_PX) {
      el.style.height = `${needed}px`;
      tall = true;
    } else {
      el.style.height = `${RESTING_H_PX}px`;
      tall = false;
    }
  }

  // Bind may land after first paint — pin resting height once the node exists.
  $effect(() => {
    if (textareaEl) untrack(() => autoresize());
  });

  function submit(): void {
    const text = value.trim();
    if (!text || pending) return;
    value = "";
    tall = false;
    queueMicrotask(() => autoresize());
    onsubmit(text);
  }

  /** Enter sends; Shift+Enter inserts a newline. Ignore IME composition Enter. */
  function handleKeydown(e: KeyboardEvent): void {
    if (e.key !== "Enter" || e.shiftKey || e.isComposing) return;
    e.preventDefault();
    submit();
  }

  const showTypewriter = $derived(value.length === 0 && animatedPlaceholder.length > 0);
  const nativePlaceholder = $derived(
    value.length === 0 && placeholderExamples.length === 0 ? placeholder : "",
  );

  /**
   * Padding owns vertical rhythm (py-2 + leading-5); inline height pins rest/grow.
   * Textareas top-align (unlike Input), so height comes from pad + line alone.
   * No drop shadow (border only, same chrome family as Input without sunk edge).
   */
  const fieldClass =
    "box-border block min-h-0 max-h-28 w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-base leading-5 transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm";

  /** Flex-center typewriter so it matches placeholder/value optical middle. */
  const overlayClass =
    "pointer-events-none absolute inset-0 flex items-center overflow-hidden text-ellipsis whitespace-nowrap px-3 text-base leading-5 text-muted-foreground md:text-sm";
</script>

<div class={cn("flex min-w-0 w-full items-center gap-2", className)}>
  <div class="relative min-h-0 min-w-0 flex-1">
    <textarea
      id={`chat-message-${uid}`}
      name="chat-message"
      bind:this={textareaEl}
      bind:value
      oninput={autoresize}
      onkeydown={handleKeydown}
      rows={1}
      placeholder={nativePlaceholder}
      aria-label={ariaLabel}
      disabled={pending}
      class={cn(fieldClass, tall ? "overflow-y-auto" : "overflow-hidden")}
    ></textarea>
    {#if showTypewriter}
      <span class={overlayClass} aria-hidden="true">
        {animatedPlaceholder}
      </span>
    {/if}
  </div>
  <Button
    type="button"
    size="icon"
    class={cn("shrink-0", tall && "self-end")}
    onclick={submit}
    disabled={!value.trim() || pending}
    aria-label={sendLabel}
    title={sendLabel}
  >
    <Send class="size-4" aria-hidden="true" />
  </Button>
</div>
