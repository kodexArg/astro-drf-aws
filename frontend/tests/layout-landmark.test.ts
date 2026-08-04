import { describe, expect, test } from "bun:test";
import { Glob } from "bun";
import path from "node:path";

// Source-level backstop for [[bdd-26-layout-main-and-fixed-header]]: the rule is
// about where `<main>` is authored, not how it renders
// ([[adr-08-frontend-and-design-system]] rule 9).

const SRC = path.join(import.meta.dir, "..", "src");
const COMPONENTS = path.join(SRC, "lib", "components");
const LAYOUTS = path.join(SRC, "layouts");

/** The one component sanctioned to author `<main>` ([[GLOSSARY]]: Page Canvas). */
const LANDMARK_OWNER = "primitives/PageCanvas.svelte";

function scan(root: string, pattern: string): string[] {
  const glob = new Glob(pattern);
  return [...glob.scanSync(root)].map((p) => p.replaceAll(path.sep, "/")).sort();
}

/** Strips comments: the rules below assert what a component renders, so prose
 * naming a forbidden thing is not itself a violation. */
function markup(source: string): string {
  return source.replace(/<!--[\s\S]*?-->/g, "").replace(/\/\*[\s\S]*?\*\//g, "");
}

async function markupOf(root: string, rel: string): Promise<string> {
  return markup(await Bun.file(path.join(root, rel)).text());
}

const components = scan(COMPONENTS, "**/*.svelte");

/**
 * A real `<main>` element, not the word inside a comment or a class name.
 * Matches the opening tag only — `<main>` or `<main ...>`.
 */
const MAIN_TAG = /<main[\s>]/;

/** `min-h-screen` anywhere in a class attribute. */
const MIN_H_SCREEN = /\bmin-h-screen\b/;

describe("bdd-26 — the layout owns the main landmark", () => {
  test("the suite discovers real subjects (a broken glob must fail, not silently pass)", () => {
    expect(components.length).toBeGreaterThan(50);
    expect(components).toContain(LANDMARK_OWNER);
  });

  test(`${LANDMARK_OWNER} is the component that authors <main>`, async () => {
    const source = await markupOf(COMPONENTS, LANDMARK_OWNER);
    expect(source).toMatch(MAIN_TAG);
  });

  for (const rel of components.filter((r) => r !== LANDMARK_OWNER)) {
    test(`${rel} does not author a <main> of its own`, async () => {
      const source = await markupOf(COMPONENTS, rel);
      expect(source).not.toMatch(MAIN_TAG);
    });
  }

  // `min-h-screen` inside a layout that already spent the header's height
  // double-counts it; `PageCanvas` owns the one viewport, as `min-h-dvh`.
  for (const rel of components) {
    test(`${rel} does not declare min-h-screen`, async () => {
      const source = await markupOf(COMPONENTS, rel);
      expect(source).not.toMatch(MIN_H_SCREEN);
    });
  }
});

describe("bdd-26 — the header is a sibling of the main", () => {
  test("Base.astro composes PageCanvas rather than authoring markup", async () => {
    const source = await markupOf(LAYOUTS, "Base.astro");

    // [[adr-08-frontend-and-design-system]] rule 9.
    expect(source).toContain("PageCanvas");
    expect(source).not.toMatch(MAIN_TAG);

    // Sibling, never nested: a <header> inside <main> silently demotes from
    // the `banner` landmark.
    const headerAt = source.indexOf("<LayoutHeader");
    const canvasAt = source.indexOf("<PageCanvas");
    expect(headerAt).toBeGreaterThan(-1);
    expect(canvasAt).toBeGreaterThan(headerAt);
    expect(source.slice(headerAt, canvasAt)).toContain("</LayoutHeader>");
  });

  // Issue #287: the header travels with the content up to its own flow
  // offset, then docks — native `position: sticky`, not `fixed`.
  test("LayoutHeader is sticky and docks to the top", async () => {
    const source = await markupOf(COMPONENTS, "header/LayoutHeader.svelte");
    expect(source).toMatch(/\bsticky\b/);
    expect(source).toMatch(/\btop-0\b/);
    expect(source).not.toMatch(/\bfixed\b/);
  });

  test("PageCanvas reserves no fixed-header clearance", async () => {
    const canvas = await markupOf(COMPONENTS, LANDMARK_OWNER);

    // The header is in-flow (sticky) since issue #287 and reserves its own
    // space; a second reservation here would double it.
    expect(canvas).not.toContain("--layout-header-height");

    // flex-1 inside body's app-shell flex column: the canvas fills exactly
    // what the header leaves — never a second viewport (phantom scroll),
    // never min-h-screen (mobile browser chrome must not push the fold).
    expect(canvas).toContain("flex-1");
    expect(canvas).not.toContain("min-h-dvh");
  });
});
