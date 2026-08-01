<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]] · [[adr-15-chatbot-two-tier]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]] · [[CHATBOT]]
     LIVE-DOC:END -->

<!--
  Transcript for both chat modes. Router outcomes stay enum-only; assistant
  answers render as text nodes (never {@html}) plus structured links only.
-->
<script lang="ts" module>
  export type ChatMessage =
    | { id: string; role: "user"; text: string }
    | { id: string; role: "navigate"; label: string; target: string }
    | { id: string; role: "confirm"; label: string; target: string }
    | { id: string; role: "status"; text: string }
    | {
        id: string;
        role: "assistant";
        text: string;
        links?: { target: string; label: string }[];
      };
</script>

<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Alert, AlertDescription } from "$lib/components/ui/alert";
  import * as Card from "$lib/components/ui/card";
  import ConfirmDialog from "$lib/components/overlay/ConfirmDialog.svelte";

  let {
    messages,
    onconfirm = undefined,
    copy,
  }: {
    messages: ChatMessage[];
    onconfirm?: (message: Extract<ChatMessage, { role: "confirm" }>) => void;
    copy: { go: string; confirm: string };
  } = $props();

  // Money-like tokens get monospace; everything else is plain text (never HTML).
  const MONEY_TOKEN = /^\$?\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?(?:\s?[kKmM])?$/;
  const MONEY_SPLIT = /(\$?\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?(?:\s?[kKmM])?)/g;

  function answerSegments(text: string): { kind: "text" | "money"; value: string }[] {
    return text
      .split(MONEY_SPLIT)
      .filter((p) => p.length > 0)
      .map((value) => ({
        kind: MONEY_TOKEN.test(value) ? ("money" as const) : ("text" as const),
        value,
      }));
  }
</script>

<div class="flex flex-col gap-3">
  {#each messages as message (message.id)}
    {#if message.role === "user"}
      <div class="flex justify-end">
        <div class="max-w-[85%] rounded-2xl rounded-br-sm bg-primary px-4 py-2 text-sm text-primary-foreground">
          {message.text}
        </div>
      </div>
    {:else if message.role === "navigate"}
      <Card.Root class="max-w-[85%] self-start">
        <Card.Content class="flex items-center justify-between gap-4 py-3">
          <span class="text-sm">{message.label}</span>
          <Button href={message.target} size="sm">{copy.go}</Button>
        </Card.Content>
      </Card.Root>
    {:else if message.role === "confirm"}
      <Card.Root class="max-w-[85%] self-start">
        <Card.Content class="flex items-center justify-between gap-4 py-3">
          <span class="text-sm">{message.label}</span>
          <ConfirmDialog
            title={message.label}
            confirmLabel={copy.confirm}
            triggerLabel={copy.confirm}
            onconfirm={() => onconfirm?.(message)}
          />
        </Card.Content>
      </Card.Root>
    {:else if message.role === "assistant"}
      <div class="flex max-w-[85%] flex-col gap-2 self-start">
        <div class="rounded-2xl rounded-bl-sm bg-muted px-4 py-2 text-sm text-foreground">
          {#each answerSegments(message.text) as seg}
            {#if seg.kind === "money"}
              <span class="font-mono tabular-nums">{seg.value}</span>
            {:else}
              {seg.value}
            {/if}
          {/each}
        </div>
        {#if message.links && message.links.length > 0}
          <div class="flex flex-wrap gap-2">
            {#each message.links as link}
              <Button href={link.target} size="sm" variant="outline">{link.label}</Button>
            {/each}
          </div>
        {/if}
      </div>
    {:else}
      <Alert class="max-w-[85%] self-start">
        <AlertDescription>{message.text}</AlertDescription>
      </Alert>
    {/if}
  {/each}
</div>
