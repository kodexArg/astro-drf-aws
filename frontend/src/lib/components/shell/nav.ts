/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
 * Governed by: [[adr-08-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

/** The single registry of the site's routes: nav drawer, home cards, and the
 * assistant's page identity all read this list and nothing else. */

import type { Component } from "svelte";
import { MessageCircle, LayoutGrid, User } from "$lib/components/icons";
import type { MessageKey } from "../../../i18n";

export interface NavItemSpec {
  href: string;
  labelKey: MessageKey;
  /** Presentation, not language — icons stay out of the i18n catalog. */
  icon: Component<{ class?: string; "aria-hidden"?: string }>;
  abstractKey: MessageKey;
}

export const NAV_ITEMS: NavItemSpec[] = [
  {
    href: "/chatui/",
    labelKey: "shell_nav_chatui",
    icon: MessageCircle,
    abstractKey: "home_card_abstract_chatui",
  },
  {
    href: "/showcase/components/",
    labelKey: "shell_nav_showcase",
    icon: LayoutGrid,
    abstractKey: "home_card_abstract_showcase",
  },
  {
    href: "/profile/",
    labelKey: "shell_nav_profile",
    icon: User,
    abstractKey: "home_card_abstract_profile",
  },
];

export interface NavSection {
  /** Omitted renders no heading — an ungrouped section. */
  titleKey?: MessageKey;
  items: NavItemSpec[];
}

/** Grouping capability over NAV_ITEMS for NavDrawer's docked/floating panel;
 * ships one ungrouped section today, ready for a titled split once the
 * route list grows past it. */
export const NAV_SECTIONS: NavSection[] = [{ items: NAV_ITEMS }];

/** Exact, not prefix: sibling routes (e.g. `/showcase/` and
 * `/showcase/components/`) would both light under a prefix match. */
export function isActive(href: string, pathname: string): boolean {
  const normalize = (value: string) => (value.endsWith("/") ? value : `${value}/`);
  return normalize(pathname) === normalize(href);
}
