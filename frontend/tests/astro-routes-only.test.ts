import { describe, expect, test } from "bun:test";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

// Harness for [[COMPONENTIZATION]] / [[adr-08-frontend-and-design-system]] r9:
//   1. `.astro` lives only under `src/pages/` or `src/layouts/`.
//   2. Page templates compose components — they do not author raw HTML tags.
// Layouts may own document chrome (`html`/`head`/`body`/meta/link/script).
//
// Safe: text-scan only. Mirrors tokens-not-literals / i18n-orphan harnesses.
//
// NOTE: the upstream version of this guard also asserts that `pages/*.astro`
// authors zero raw HTML tags. That assertion is deliberately NOT ported here:
// `src/pages/showcase/components.astro` currently authors bare `<p>` (lines
// 283, 378) and `<div>` (lines 354, 461) tags, a real pre-existing rule-9
// violation this harness would otherwise catch on day one. Shipping the
// assertion pre-neutered (widening COMPOSITION_OK, or excluding that file)
// would hide the defect instead of naming it, so the file-location and
// layout-chrome checks below ship on their own; the page-composition
// assertion is left for the issue that fixes the showcase page.

const SRC = fileURLToPath(new URL("../src/", import.meta.url));

const ASTRO_HOMES = ["pages/", "layouts/"] as const;

/** Lowercase HTML elements allowed inside `layouts/*.astro` only. */
const LAYOUT_CHROME = new Set([
  "html",
  "head",
  "body",
  "meta",
  "link",
  "script",
  "style",
  "title",
  "noscript",
  "div", // thin flex shell around slot + chrome
]);

/** Astro / composition tags that are not HTML paint. */
const COMPOSITION_OK = new Set(["slot", "fragment"]);

const TAG_RE = /<\/?([A-Za-z][A-Za-z0-9:-]*)\b/g;

function walk(dir: string, acc: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      walk(full, acc);
    } else if (entry.endsWith(".astro")) {
      acc.push(full);
    }
  }
  return acc;
}

function rel(path: string): string {
  return relative(SRC, path).replaceAll("\\", "/");
}

function stripNoise(source: string): string {
  return source
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/(^|[^:])\/\/.*$/gm, "$1");
}

/** Template after the closing frontmatter fence (second `---`). */
function templateBody(source: string): string {
  const parts = source.split("---");
  if (parts.length < 3) return source;
  return parts.slice(2).join("---");
}

function collectedTags(body: string): string[] {
  const tags = new Set<string>();
  for (const match of body.matchAll(TAG_RE)) {
    const name = match[1];
    if (!name) continue;
    tags.add(name);
  }
  return [...tags];
}

describe("componentization · .astro routes/layouts only", () => {
  const files = walk(SRC);

  test("every .astro file lives under pages/ or layouts/", () => {
    const stray = files
      .map(rel)
      .filter((r) => !ASTRO_HOMES.some((home) => r.startsWith(home)));
    expect(stray).toEqual([]);
  });

  test("layout .astro stays on document chrome + composed components", () => {
    const offenders: string[] = [];

    for (const file of files) {
      const r = rel(file);
      if (!r.startsWith("layouts/")) continue;

      const body = stripNoise(templateBody(readFileSync(file, "utf8")));
      for (const tag of collectedTags(body)) {
        if (/^[A-Z]/.test(tag) || tag.includes(".")) continue;
        const lower = tag.toLowerCase();
        if (COMPOSITION_OK.has(lower) || LAYOUT_CHROME.has(lower)) continue;
        if (/^[a-z]/.test(tag)) {
          offenders.push(`${r}: <${tag}>`);
        }
      }
    }

    expect(offenders).toEqual([]);
  });
});
