<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]] · [[adr-17-chatbot-two-tier]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]] · [[CHATBOT]]
     LIVE-DOC:END -->

<!--
  One chat component, two modes (kdx-chatui). Default `router` posts to
  POST /api/router/route/ and renders closed-enum outcomes only. `assistant`
  posts to POST /api/assistant/ask/ with a page identity and renders free-text
  answers as text nodes plus structured links — never confirm/actuators.
-->
<script lang="ts">
  import ChatMessageList, { type ChatMessage } from "./ChatMessageList.svelte";
  import ChatComposer from "./ChatComposer.svelte";
  import { routeUtterance, copyForResult, resolveConfirmUrl } from "$lib/router-client";
  import { askAssistant, statusKeyForAskResult } from "$lib/assistant-client";
  import { readCsrfTokenFromCookie } from "$lib/csrf";

  type ChatUICopy = {
    title: string;
    composerPlaceholder: string;
    composerAriaLabel: string;
    composerSend: string;
    composerPlaceholderExamples?: string[];
    messageGo: string;
    messageConfirm: string;
    outcomeCopy: Record<string, string>;
  };

  const EMPTY_COPY: ChatUICopy = {
    title: "",
    composerPlaceholder: "",
    composerAriaLabel: "",
    composerSend: "",
    messageGo: "",
    messageConfirm: "",
    outcomeCopy: {},
  };

  let {
    class: className = undefined,
    publicBackendUrl = "",
    copy = EMPTY_COPY,
    mode = "router",
    page = "/",
  }: {
    class?: string;
    publicBackendUrl?: string;
    copy?: ChatUICopy;
    /** `router` (default) or `assistant` — one component, two modes. */
    mode?: "router" | "assistant";
    /** Closed nav-registry path for assistant mode (server-side context key). */
    page?: string;
  } = $props();

  let messages = $state<ChatMessage[]>([]);
  let pending = $state(false);
  let seq = 0;
  let messageContainer: HTMLDivElement | undefined = $state(undefined);

  function push(message: Omit<ChatMessage, "id">): void {
    messages = [...messages, { ...message, id: String(seq++) } as ChatMessage];
  }

  $effect(() => {
    messages.length;
    if (messageContainer) messageContainer.scrollTop = messageContainer.scrollHeight;
  });

  async function handleSubmitRouter(text: string): Promise<void> {
    const result = await routeUtterance(publicBackendUrl, text, readCsrfTokenFromCookie());

    if (result.kind === "outcome" && result.data.outcome === "Action") {
      const action = result.data.action;
      if (action.kind === "navigate") {
        push({ role: "navigate", label: action.label, target: action.target });
      } else {
        push({ role: "confirm", label: action.label, target: action.target });
      }
      return;
    }

    const outcomeKey = copyForResult(result);
    push({ role: "status", text: (outcomeKey && copy.outcomeCopy[outcomeKey]) ?? "" });
  }

  async function handleSubmitAssistant(text: string): Promise<void> {
    const result = await askAssistant(
      publicBackendUrl,
      text,
      page,
      readCsrfTokenFromCookie(),
    );

    if (result.kind === "answer") {
      push({
        role: "assistant",
        text: result.data.answer,
        links: result.data.links,
      });
      return;
    }

    const statusKey = statusKeyForAskResult(result);
    push({ role: "status", text: (statusKey && copy.outcomeCopy[statusKey]) ?? "" });
  }

  async function handleSubmit(text: string): Promise<void> {
    push({ role: "user", text });
    pending = true;
    try {
      if (mode === "assistant") {
        await handleSubmitAssistant(text);
      } else {
        await handleSubmitRouter(text);
      }
    } finally {
      pending = false;
    }
  }

  function confirmNavigate(message: Extract<ChatMessage, { role: "confirm" }>): void {
    // Assistant mode never emits confirm; guard keeps zero-prop mounts safe.
    if (mode === "assistant") return;

    const form = document.createElement("form");
    form.method = "post";
    form.action = resolveConfirmUrl(publicBackendUrl, message.target);
    form.hidden = true;

    const token = document.createElement("input");
    token.type = "hidden";
    token.name = "csrfmiddlewaretoken";
    token.value = readCsrfTokenFromCookie();
    form.appendChild(token);

    document.body.appendChild(form);
    form.submit();
  }
</script>

<div
  class={`mx-auto flex min-h-0 w-full min-w-0 max-w-2xl flex-1 flex-col gap-4 overflow-x-hidden px-4 py-8 ${className ?? ""}`}
  data-chat-mode={mode}
>
  <div
    bind:this={messageContainer}
    class="flex min-h-0 flex-1 flex-col justify-end overflow-y-auto"
  >
    {#if messages.length > 0}
      <ChatMessageList
        {messages}
        onconfirm={mode === "router" ? confirmNavigate : undefined}
        copy={{ go: copy.messageGo, confirm: copy.messageConfirm }}
      />
    {/if}
  </div>
  <div class="flex shrink-0 flex-col gap-2">
    <ChatComposer
      {pending}
      onsubmit={handleSubmit}
      placeholder={copy.composerPlaceholder}
      ariaLabel={copy.composerAriaLabel}
      sendLabel={copy.composerSend}
      placeholderExamples={copy.composerPlaceholderExamples ?? []}
    />
  </div>
</div>
