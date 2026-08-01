<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Composition only: overlay/Drawer + chat/ChatUI in assistant mode.
  Side is the mirror of the nav drawer's sidebarSide — never a second hard edge.
-->
<script lang="ts">
  import Drawer from "$lib/components/overlay/Drawer.svelte";
  import ChatUI from "$lib/components/chat/ChatUI.svelte";
  import { t } from "../../../i18n";
  import type { SidebarSide } from "$lib/theme";

  type ChatCopy = {
    title: string;
    composerPlaceholder: string;
    composerAriaLabel: string;
    composerSend: string;
    composerPlaceholderExamples?: string[];
    messageGo: string;
    messageConfirm: string;
    outcomeCopy: Record<string, string>;
  };

  const EMPTY_COPY: ChatCopy = {
    title: "",
    composerPlaceholder: "",
    composerAriaLabel: "",
    composerSend: "",
    messageGo: "",
    messageConfirm: "",
    outcomeCopy: {},
  };

  let {
    side = "left",
    page = "/",
    publicBackendUrl = "",
    copy = EMPTY_COPY,
    open = $bindable(false),
  }: {
    /** Mirror of nav `sidebarSide` — derived by the layout, never hardcoded. */
    side?: SidebarSide;
    /** Closed nav-registry path for server-side assistant context. */
    page?: string;
    publicBackendUrl?: string;
    copy?: ChatCopy;
    open?: boolean;
  } = $props();
</script>

<Drawer
  bind:open
  {side}
  width="22rem"
  title={copy.title || t("chatui_assistant_title")}
  openLabel={t("shell_chat_drawer_label")}
  closeLabel={t("drawer_close")}
>
  <div class="flex min-h-0 flex-1 flex-col">
    <ChatUI
      mode="assistant"
      {page}
      {publicBackendUrl}
      {copy}
      class="max-w-none flex-1 px-0 py-0"
    />
  </div>
</Drawer>
