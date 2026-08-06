/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
 * Governed by: [[adr-08-frontend-and-design-system]] · [[adr-28-nav-fsm-frosted-rail]]
 * Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]]
 * LIVE-DOC:END */

/**
 * Closed shell panel widths. Rem values live in `app.css` as
 * `--shell-aside-*` / `--shell-drawer-*`; drawer M/S alias aside M/S so the
 * medium and small steps stay identical across both surfaces.
 */

/** Locked rail / shell-menu FancyDrawer density. Default M. */
export type AsideSize = "L" | "M" | "S";

/** Overlay Drawer (and ChatDrawer) density. Default L; XL is drawer-only. */
export type DrawerSize = "XL" | "L" | "M" | "S";

export const ASIDE_SIZE_VAR: Record<AsideSize, string> = {
  L: "var(--shell-aside-l)",
  M: "var(--shell-aside-m)",
  S: "var(--shell-aside-s)",
};

export const DRAWER_SIZE_VAR: Record<DrawerSize, string> = {
  XL: "var(--shell-drawer-xl)",
  L: "var(--shell-drawer-l)",
  M: "var(--shell-drawer-m)",
  S: "var(--shell-drawer-s)",
};
