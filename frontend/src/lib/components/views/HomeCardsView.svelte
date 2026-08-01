<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
     Governed by: [[adr-04-frontend-and-design-system]] · [[adr-22-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  The home ("/") body — a single-column list of HomeCard links onto the
  site's routes, one per NAV_ITEMS row (shell/nav.ts). Keeps the lobby's
  pending/denied states intact ([[adr-20-authorization-lobby]]): a role-less
  session still sees only the pending card, never the route links, since
  every card's target route bounces it back to `/` with `?denied=1` anyway.
  `items` arrives already localized — this component imports no i18n of its
  own.
-->
<script lang="ts">
  import * as Card from "$lib/components/ui/card";
  import { Alert, AlertTitle, AlertDescription } from "$lib/components/ui/alert";
  import HomeCard from "./HomeCard.svelte";
  import type { Component } from "svelte";

  type HomeCopy = {
    deniedTitle: string;
    deniedBody: string;
    pendingTitle: string;
    pendingBody: string;
    cardsTitle: string;
  };

  type HomeCardItem = {
    href: string;
    /** Lucide icon component from `$lib/components/icons` ([[FRONTEND]]) — never an emoji glyph. */
    icon: Component<{ class?: string; "aria-hidden"?: string }>;
    title: string;
    abstract: string;
  };

  let {
    denied = false,
    pending = false,
    copy = {} as HomeCopy,
    items = [] as HomeCardItem[],
  }: {
    denied?: boolean;
    pending?: boolean;
    copy?: HomeCopy;
    items?: HomeCardItem[];
  } = $props();
</script>

<!--
  No chrome of its own: the header and the `<main>` are the layout's now,
  supplied once by `LayoutHeader` and `PageCanvas`; duplicating them here
  would give any page that remounted this component two banners and two
  landmarks.
-->
<div class="flex flex-1 flex-col">
  <div class="flex flex-1 flex-col items-center gap-8 px-6 py-12">
    {#if denied}
      <Alert variant="destructive" class="w-full max-w-xl">
        <AlertTitle>{copy.deniedTitle}</AlertTitle>
        <AlertDescription>{copy.deniedBody}</AlertDescription>
      </Alert>
    {/if}

    {#if pending}
      <Card.Root class="w-full max-w-sm border-border/40 shadow-sm">
        <Card.Header>
          <Card.Title>{copy.pendingTitle}</Card.Title>
        </Card.Header>
        <Card.Content>
          <p class="text-sm text-muted-foreground">{copy.pendingBody}</p>
        </Card.Content>
      </Card.Root>
    {:else}

      <ul class="flex w-full max-w-xl flex-col gap-3">
        {#each items as item (item.href)}
          <li>
            <HomeCard href={item.href} icon={item.icon} title={item.title} abstract={item.abstract} />
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</div>
