import { describe, expect, test } from "bun:test";
import { Glob } from "bun";
import path from "node:path";

// adr-08 rule 9: a `.astro` page/layout composes components and holds
// page-level wiring; it authors no non-trivial markup of its own. Only the
// `<main>` landmark slice was checked before (layout-landmark.test.ts) — this
// enforces the general rule.
//
// "non-trivial markup" is defined precisely, so the rule is mechanical: any
// literal text run sitting directly between two tags in the rendered
// template (frontmatter excluded), once whitespace and `{expression}`
// interpolations are stripped, is authored prose. A page delegates all copy
// to `.svelte` components / i18n `t()` calls, so a real page never leaves one.

const SRC = path.join(import.meta.dir, "..", "src");

function scan(pattern: string): string[] {
  const glob = new Glob(pattern);
  return [...glob.scanSync(SRC)].map((p) => p.replaceAll(path.sep, "/")).sort();
}

/** Strips frontmatter (server-only code, not the rendered template). */
function templateOf(source: string): string {
  const first = source.indexOf("---");
  if (first === -1) return source;
  const second = source.indexOf("---", first + 3);
  if (second === -1) return source;
  return source.slice(second + 3);
}

/** Balanced `{...}` removal — an expression may itself hold nested tags
 * (`{cond && (<Foo />)}`), so a non-nesting regex would mis-split it. */
function stripExpressions(template: string): string {
  let out = "";
  let depth = 0;
  for (const ch of template) {
    if (ch === "{") {
      depth++;
      continue;
    }
    if (ch === "}") {
      if (depth > 0) depth--;
      continue;
    }
    if (depth === 0) out += ch;
  }
  return out;
}

function stripNoise(template: string): string {
  return stripExpressions(
    template
      .replace(/<!--[\s\S]*?-->/g, "")
      .replace(/<script[\s\S]*?<\/script>/gi, "<script></script>")
      .replace(/<style[\s\S]*?<\/style>/gi, "<style></style>"),
  );
}

/** A literal text run between two tags, once expressions and whitespace are
 * removed. Non-empty means authored prose lives inline. */
function literalTextRuns(template: string): string[] {
  const clean = stripNoise(template);
  const runs: string[] = [];
  for (const m of clean.matchAll(/>([^<]*)</g)) {
    const stripped = m[1].trim();
    if (stripped.length > 0) runs.push(stripped);
  }
  return runs;
}

const pages = scan("pages/**/*.astro");
const layouts = scan("layouts/**/*.astro");
const files = [...pages, ...layouts];

describe("adr-08 rule 9 — pages/layouts author no non-trivial markup", () => {
  test("the suite discovers real subjects", () => {
    expect(pages.length).toBeGreaterThan(0);
    expect(layouts.length).toBeGreaterThan(0);
  });

  test("the detector catches a literal prose block and ignores expressions", () => {
    expect(literalTextRuns("<div>Hello world</div>")).toEqual(["Hello world"]);
    expect(literalTextRuns('<div>{t("key")}</div>')).toEqual([]);
    expect(literalTextRuns("<div>\n  \n</div>")).toEqual([]);
    expect(literalTextRuns("<Foo>{title}</Foo><Bar />")).toEqual([]);
  });

  for (const rel of files) {
    test(`${rel} inlines no literal text between tags`, async () => {
      const source = await Bun.file(path.join(SRC, rel)).text();
      const offenders = literalTextRuns(templateOf(source));
      expect(`${rel}: ${offenders.join(" | ")}`).toBe(`${rel}: `);
    });
  }
});
