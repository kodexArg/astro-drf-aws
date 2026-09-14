/* LIVE-DOC:START — astro-drf-aws live-doc; see [[HARNESS]]
 * Governed by: [[adr-08-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

export const defaultLocale = "es";

export const locales = [defaultLocale] as const;

export type Locale = (typeof locales)[number];
