/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
 * Governed by: [[adr-08-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

import type { ThemeConfig } from "$lib/theme";

export interface Me {
  sub: string;
  email: string;
  given_name: string;
  family_name: string;
  picture: string;
  groups: string[];
  nickname: string;
  avatar_visible: boolean;
  /** Opt-in page-context ChatDrawer; default false for every user. */
  chat_drawer_enabled: boolean;
  theme_config?: ThemeConfig;
}
