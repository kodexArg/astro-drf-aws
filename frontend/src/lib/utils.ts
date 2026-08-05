/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
 * Governed by: [[adr-08-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

import { twMerge } from "tailwind-merge";

export type ClassValue = string | false | null | undefined;


export function cn(...classes: ClassValue[]): string {
  return twMerge(classes.filter(Boolean).join(" "));
}
