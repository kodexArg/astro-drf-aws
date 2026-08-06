<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Session status card: who is signed in, which Django groups they hold, and
  login/logout. Owns a single Card.Title — callers (e.g. the component gallery)
  must not wrap it in another "Sesión" heading.
-->
<script lang="ts">
  import { onMount } from "svelte";
  import { Button } from "$lib/components/ui/button";
  import * as Card from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  import { readCsrfTokenFromCookie } from "$lib/csrf";
  import { resolveDisplayName } from "$lib/display-name";
  import type { Me } from "$lib/types/user";

  type AuthPanelCopy = {
    title: string;
    loggedInAs: string;
    noGroups: string;
    notSignedIn: string;
    login: string;
    logout: string;
  };

  let {
    me = null,
    publicBackendUrl = "",
    copy = {} as AuthPanelCopy,
  }: {
    me?: Me | null;
    publicBackendUrl?: string;
    /** Rendered copy arrives resolved from the page's frontmatter (LOCALIZATION) */
    copy?: AuthPanelCopy;
  } = $props();

  const username = $derived(resolveDisplayName(me));

  let csrfToken = $state("");

  onMount(() => {
    csrfToken = readCsrfTokenFromCookie();
  });
</script>

<Card.Root class="max-w-lg">
  <Card.Header>
    <Card.Title>{copy.title}</Card.Title>
  </Card.Header>
  <Card.Content class="flex flex-col gap-4">
    {#if me}
      <p class="text-sm text-foreground">
        {copy.loggedInAs}
        <strong class="font-semibold">{username || me.sub}</strong>
      </p>
      <div class="flex flex-wrap gap-2" aria-label={copy.title}>
        {#if me.groups.length > 0}
          {#each me.groups as g (g)}
            <Badge variant="secondary">{g}</Badge>
          {/each}
        {:else}
          <span class="text-sm text-muted-foreground">{copy.noGroups}</span>
        {/if}
      </div>
      <form method="post" action={`${publicBackendUrl}/accounts/logout/`}>
        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
        <Button type="submit" variant="destructive">{copy.logout}</Button>
      </form>
    {:else}
      <p class="text-sm text-muted-foreground">{copy.notSignedIn}</p>
      <Button href={`${publicBackendUrl}/accounts/login/`}>{copy.login}</Button>
    {/if}
  </Card.Content>
</Card.Root>
