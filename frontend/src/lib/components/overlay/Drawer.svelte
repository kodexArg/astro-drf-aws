<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Shell stacking: ClientRouter view transitions hoist named snapshots into a
  layer above the live DOM. A fixed drawer with only document z-40 is
  covered by `page-main`'s snapshot during navigation. A caller composing
  this into shell chrome passes `viewTransitionName` (ChatDrawer: `shell-chat`)
  so this <aside> itself joins that layer; app.css stacks
  `::view-transition-group(shell-chat)` above `page-main`. The name must
  live on this fixed root — never on an Astro island wrapper — or the
  captured box misses the overlay. Empty (the default) keeps showcase/demo
  mounts out of the VT layer, since two elements can never share one
  `view-transition-name`.
-->
<script lang="ts">
  import { cn } from "$lib/utils";
  import { ChevronLeft, ChevronRight } from "$lib/components/icons";
  import { DRAWER_SIZE_VAR, type DrawerSize } from "$lib/components/shell/shell-sizes";
  import { t } from "../../../i18n";
  import type { Snippet } from "svelte";

  let {
    open = $bindable(false),
    side = "left",
    title = "",
    /**
     * Panel width: XL (22rem) | L (18rem, default) | M (11rem, = aside M) | S (9rem, = aside S).
     * Tokens: `--shell-drawer-*` in `app.css`.
     */
    size = "L" as DrawerSize,
    openLabel = t("drawer_open"),
    closeLabel = t("drawer_close"),
    /** Optional peek-tab content; defaults to open/close carets. */
    peekIcon,
    /**
     * CSS `view-transition-name` for shell chrome composing this drawer.
     * Empty keeps showcase / demos out of the VT layer.
     */
    viewTransitionName = "",
    children,
    class: className = undefined,
  }: {
    open?: boolean;
    side?: "left" | "right";
    title?: string;
    size?: DrawerSize;
    openLabel?: string;
    closeLabel?: string;
    peekIcon?: Snippet;
    viewTransitionName?: string;
    children?: Snippet;
    class?: string;
  } = $props();

  const isLeft = $derived(side === "left");
  const offClass = $derived(isLeft ? "-translate-x-full" : "translate-x-full");
  const Caret = $derived(
    isLeft ? (open ? ChevronLeft : ChevronRight) : open ? ChevronRight : ChevronLeft,
  );
  const width = $derived(DRAWER_SIZE_VAR[size]);
  const rootStyle = $derived(
    [
      `width: ${width}`,
      viewTransitionName.trim() ? `view-transition-name: ${viewTransitionName.trim()}` : "",
    ]
      .filter(Boolean)
      .join("; "),
  );
</script>

<aside
  class={cn(
    "fixed inset-y-0 z-40 flex transition-transform duration-base ease-out motion-reduce:transition-none",
    isLeft ? "left-0" : "right-0",
    !open && offClass,
    className,
  )}
  data-drawer-size={size}
  style={rootStyle}
>
  <div
    inert={!open}
    aria-hidden={!open}
    class={cn(
      /* h-full + min-h-0: fill the fixed aside so flex children (ChatUI) can
         dock their composer and scroll the transcript internally. */
      "flex h-full min-h-0 min-w-0 flex-1 flex-col gap-4 overflow-y-auto bg-background p-4 shadow-xl",
      isLeft ? "border-r border-border" : "border-l border-border",
    )}
  >
    {#if title}
      <h2 class="truncate text-sm font-semibold text-foreground">{title}</h2>
    {/if}

    {#if children}
      {@render children()}
    {:else}
      <p class="text-sm text-muted-foreground">{t("drawer_empty")}</p>
    {/if}
  </div>

  <button
    type="button"
    onclick={() => (open = !open)}
    aria-label={open ? closeLabel : openLabel}
    aria-expanded={open}
    class={cn(
      /* Peek tab: same chrome as FancyDrawer (h-12 w-7, 2xl outer radius). */
      "absolute top-1/2 flex h-12 w-7 -translate-y-1/2 cursor-pointer items-center justify-center border border-border bg-background text-muted-foreground shadow-md transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
      isLeft
        ? "left-full rounded-r-2xl border-l-0"
        : "right-full rounded-l-2xl border-r-0",
    )}
  >
    {#if peekIcon}
      {@render peekIcon()}
    {:else}
      <Caret class="size-4" aria-hidden="true" />
    {/if}
  </button>
</aside>
