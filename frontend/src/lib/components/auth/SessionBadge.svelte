<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<!--
  Compact pill badge (avatar | display name | hamburger). The hamburger
  opens a Melt UI Popover ([[MELT-UI]]) used as a dropdown menu, hand-rolled
  directly on `melt/builders` — the same precedent nav/DropdownMenu.svelte
  sets — rather than composed from the vendored overlay/Popover component:
  that component's trigger self-renders a fixed labeled Button, which
  cannot host this badge's avatar+name+hamburger cluster.

  Content sits behind Melt's native `popover="manual"` attribute
  (getPopover(), Popover builder source), which is hidden-by-default per
  the HTML Popover API — first paint never shows it open, only a user
  click calls `showPopover()`. The popover-content divs therefore carry
  `[&:popover-open]:flex` in place of a bare `flex`: `display: flex`
  applies ONLY in the open state; the UA's built-in
  `[popover]:not(:popover-open) { display: none }` default governs the
  closed state, unopposed by an author-stylesheet `flex` rule.
-->
<script lang="ts">
  import { onMount } from "svelte";
  import { Popover } from "melt/builders";
  import { Button } from "$lib/components/ui/button";
  import { Avatar, AvatarImage, AvatarFallback } from "$lib/components/ui/avatar";
  import QuickThemeToggle from "$lib/components/theme/QuickThemeToggle.svelte";
  import { Mail } from "$lib/components/icons";
  import { readCsrfTokenFromCookie } from "$lib/csrf";
  import { resolveDisplayName, resolveInitials } from "$lib/display-name";
  import { cn } from "$lib/utils";
  import { sanitizeThemeConfig, writeThemeCookie, type ThemeConfig } from "$lib/theme";
  import { t } from "../../../i18n";
  import type { Me } from "$lib/types/user";

  let {
    me = null,
    pending = false,
    publicBackendUrl = "",
    loginHref = "#",
    panelHref = "#",
    logoutAction = "",
    loginLabel = "",
    logoutLabel = "",
    onLogout,
  }: {
    me?: Me | null;
    /** True for an authenticated, role-less (lobby-confined) session — gates
     * the profile deep-link, since /profile/ itself redirects a pending
     * session back to / ([[adr-21-authorization-lobby]]). Defaults to
     * `false`, the more common/demo-friendly default: a bare
     * `<SessionBadge me={demoMe} />` invocation shows the profile link, a
     * plain `<a href>` navigation, not a mutating action (adr-22 rule 2). */
    pending?: boolean;
    /** Backend origin the theme persist PATCHes (`{backend}/api/me/`). */
    publicBackendUrl?: string;
    /** Real login route; caller-wired, defaults to inert (adr-22 rule 2). */
    loginHref?: string;
    /** Real /profile/ route; caller-wired, defaults to inert. */
    panelHref?: string;
    /** Real logout POST target; empty leaves the form a safe no-op on submit. */
    logoutAction?: string;
    /** Rendered copy arrives resolved from the page's frontmatter (LOCALIZATION) */
    loginLabel?: string;
    logoutLabel?: string;
    /** Called instead of submitting the logout form when supplied — lets a
     * caller (e.g. a gallery demo) intercept the mutating action. Defaults
     * to `undefined`, which leaves the real form submit as the action, so a
     * bare `<SessionBadge me={demoMe} />` invocation with no `me` (adr-22 r1
     * default `null`) never reaches this path in the first place. */
    onLogout?: (event: SubmitEvent) => void;
  } = $props();

  const username = $derived(resolveDisplayName(me));
  const initials = $derived(resolveInitials(me));

  let csrfToken = $state("");

  onMount(() => {
    csrfToken = readCsrfTokenFromCookie();
  });

  function handleLogoutSubmit(event: SubmitEvent): void {
    if (onLogout) {
      event.preventDefault();
      onLogout(event);
      return;
    }
    if (!logoutAction) event.preventDefault();
  }

  // Reconciles theme_config — the DB confirms the write, then the cookie is
  // rewritten from that response so it converges on the server-confirmed
  // value; a failed PATCH leaves the optimistic cookie in place until the
  // next login or PATCH ([[adr-21-authorization-lobby]]).
  async function persistTheme(blob: ThemeConfig): Promise<void> {
    try {
      const res = await fetch(`${publicBackendUrl}/api/me/`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": readCsrfTokenFromCookie(),
        },
        body: JSON.stringify({ theme_config: blob }),
      });
      if (!res.ok) {
        console.warn("theme_config persist rejected", res.status);
        return;
      }
      const confirmed = sanitizeThemeConfig(((await res.json()) as Me).theme_config);
      writeThemeCookie(confirmed);
    } catch (err) {
      // Never surfaced to the user: the cookie already painted, and the DB
      // wins at the next login/PATCH reconciliation.
      console.warn("theme_config persist failed; cookie is ahead of the DB", err);
    }
  }

  const popover = new Popover({
    floatingConfig: {
      computePosition: { placement: "bottom-end" },
    },
  });
</script>

{#if me}
  <button
    type="button"
    {...popover.trigger}
    aria-label={t("auth_open_menu")}
    class={cn(
      "flex h-9 items-center gap-2 rounded-full border border-border bg-card pl-1 pr-2 text-card-foreground shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
    )}
  >
    <Avatar class="size-7">
      {#if me.picture}
        <AvatarImage src={me.picture} alt={username} />
      {:else}
        <AvatarFallback class="text-xs">{initials}</AvatarFallback>
      {/if}
    </Avatar>
    <span class="max-w-32 truncate text-sm font-medium">{username}</span>
    <span aria-hidden="true" class="text-muted-foreground">&#9776;</span>
  </button>

  <div
    {...popover.content}
    class="z-50 hidden min-w-56 flex-col gap-3 rounded-md border border-border bg-popover p-3 text-popover-foreground shadow-md [&:popover-open]:flex"
  >
    <span class="flex items-center gap-2 text-sm text-muted-foreground">
      <Mail class="size-4" aria-hidden="true" />
      <span class="truncate">{me.email}</span>
    </span>
    <QuickThemeToggle label={t("theme_toggle_mode")} onPersist={persistTheme} />
    {#if !pending}
      <Button href={panelHref} variant="ghost" size="sm" class="h-9 w-full justify-start gap-2">
        <span aria-hidden="true">{"\u{1F39B}"}</span>
        {t("nav_profile")}
      </Button>
    {/if}
    <form method="post" action={logoutAction || "#"} onsubmit={handleLogoutSubmit}>
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
      <Button type="submit" variant="destructive" size="sm" class="h-9 w-full justify-start gap-2">
        <span aria-hidden="true">{"\u{1F6AA}"}</span>
        {logoutLabel}
      </Button>
    </form>
  </div>
{:else}
  <div class="flex items-center gap-2">
    <button
      type="button"
      {...popover.trigger}
      aria-label={t("auth_open_menu")}
      class={cn(
        "inline-flex size-9 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
      )}
    >
      <span aria-hidden="true">&#9776;</span>
    </button>
    <Button href={loginHref} class="rounded-full">{loginLabel}</Button>
  </div>

  <div
    {...popover.content}
    class="z-50 hidden min-w-40 flex-col gap-3 rounded-md border border-border bg-popover p-3 text-popover-foreground shadow-md [&:popover-open]:flex"
  >
    <QuickThemeToggle label={t("theme_toggle_mode")} />
  </div>
{/if}
