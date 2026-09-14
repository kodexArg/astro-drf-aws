/* LIVE-DOC:START — astro-drf-aws live-doc; see [[HARNESS]]
 * Governed by: [[adr-08-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

import type { Me } from "./types/user";

export function hasRole(me: Me | null): me is Me {
  return me !== null && me.groups.length > 0;
}
