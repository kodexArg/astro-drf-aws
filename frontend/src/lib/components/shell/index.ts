/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
 * Governed by: [[adr-08-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

export { default as NavItem } from "./NavItem.svelte";
export { default as NavBadge } from "./NavBadge.svelte";
export { default as NavDrawer } from "./NavDrawer.svelte";
export { default as ChatDrawer } from "./ChatDrawer.svelte";
export { default as NavbarIcon } from "./NavbarIcon.svelte";

export { NAV_ITEMS, isActive } from "./nav";
export type { NavItemSpec } from "./nav";

export {
  parseNavLockCookie,
  resolveNavFsm,
  resolvePresentation,
  NAV_LOCK_COOKIE,
  RAIL_MIN_WIDTH,
} from "./nav-fsm";
export type {
  NavLockPreference,
  NavPresentation,
  NavFsmState,
} from "./nav-fsm";

export { ASIDE_SIZE_VAR, DRAWER_SIZE_VAR } from "./shell-sizes";
export type { AsideSize, DrawerSize } from "./shell-sizes";
