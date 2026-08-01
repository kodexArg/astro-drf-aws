<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]] · [[adr-15-chatbot-two-tier]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]] · [[CHATBOT]]
     LIVE-DOC:END -->

<!--
  The composer only collects the user's raw utterance and hands it up via
  `onsubmit` ([[CHATBOT]]). It never renders assistant text and holds no
  actuator rights — the two-tier split (adr-15) lives above it in ChatUI.
-->
<script lang="ts">
  import { onDestroy } from "svelte";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import { Send } from "$lib/components/icons";
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

  let value = $state("");
  let animatedPlaceholder = $state("");

  const realScheduler: Scheduler = {
    set: (cb, ms) => setTimeout(cb, ms),
    clear: (handle) => clearTimeout(handle as ReturnType<typeof setTimeout>),
  };

  const cycle = createTypewriterCycle(
    placeholderExamples,
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

  function submit(): void {
    const text = value.trim();
    if (!text || pending) return;
    value = "";
    onsubmit(text);
  }

  function handleKeydown(e: KeyboardEvent): void {
    if (e.key === "Enter") {
      e.preventDefault();
      submit();
    }
  }
</script>

<div class={`flex min-w-0 w-full items-center gap-2 ${className ?? ""}`}>
  <div class="relative min-w-0 flex-1">
    <Input
      id={`chat-message-${uid}`}
      name="chat-message"
      bind:value
      onkeydown={handleKeydown}
      placeholder={value.length === 0 && placeholderExamples.length === 0 ? placeholder : ""}
      aria-label={ariaLabel}
      disabled={pending}
      class="min-w-0"
    />
    {#if value.length === 0 && animatedPlaceholder}
      <span
        class="pointer-events-none absolute inset-y-0 left-3 right-3 flex items-center overflow-hidden text-ellipsis whitespace-nowrap text-sm text-muted-foreground"
      >
        {animatedPlaceholder}
      </span>
    {/if}
  </div>
  <Button type="button" class="shrink-0" onclick={submit} disabled={!value.trim() || pending}>
    <Send class="size-4" aria-hidden="true" />
    {sendLabel}
  </Button>
</div>
