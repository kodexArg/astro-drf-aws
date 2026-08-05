/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
 * Governed by: [[adr-08-frontend-and-design-system]] · [[adr-14-auth]] · [[adr-09-htmx]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

export function readCsrfTokenFromCookie(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}
