import { describe, expect, test } from "bun:test";
import path from "node:path";

// Source-level contract tests for the view-transition stacking contract
// ([[adr-28-nav-fsm-frosted-rail]]): fixed shell chrome carries its own
// `view-transition-name` on the fixed root it renders — never on the Astro
// island wrapper — stacked above the page-content VT group, with the
// `transition:persist` id kept distinct from that group name. DOM-mount
// behavior (zero-props, no throw) is covered by component-mount.test.ts's
// self-discovering glob; this file checks the source text for the wiring
// that a DOM mount alone cannot observe (Astro-side transition directives,
// CSS group selectors).

const ROOT = path.join(import.meta.dir, "..");
const BASE_ASTRO = path.join(ROOT, "src", "layouts", "Base.astro");
const NAV_DRAWER = path.join(ROOT, "src", "lib", "components", "shell", "NavDrawer.svelte");
const CHAT_DRAWER = path.join(ROOT, "src", "lib", "components", "shell", "ChatDrawer.svelte");
const DRAWER = path.join(ROOT, "src", "lib", "components", "overlay", "Drawer.svelte");
const FANCY_DRAWER = path.join(ROOT, "src", "lib", "components", "overlay", "FancyDrawer.svelte");
const APP_CSS = path.join(ROOT, "src", "styles", "app.css");

async function read(file: string): Promise<string> {
  return Bun.file(file).text();
}

describe("Drawer / FancyDrawer — viewTransitionName is optional and defaults empty", () => {
  test("Drawer.svelte takes an optional viewTransitionName prop, defaulted empty", async () => {
    const source = await read(DRAWER);
    expect(source).toMatch(/viewTransitionName\s*=\s*""/);
  });

  test("Drawer.svelte applies it to the fixed <aside> root only when non-empty", async () => {
    const source = await read(DRAWER);
    expect(source).toContain("view-transition-name: ${viewTransitionName.trim()}");
    // The prop drives the <aside>'s own style, not a child.
    const asideIndex = source.indexOf("<aside");
    const styleIndex = source.indexOf("style={rootStyle}");
    expect(styleIndex).toBeGreaterThan(asideIndex);
  });

  test("FancyDrawer.svelte takes an optional viewTransitionName prop, defaulted empty", async () => {
    const source = await read(FANCY_DRAWER);
    expect(source).toMatch(/viewTransitionName\s*=\s*""/);
  });

  test("FancyDrawer.svelte applies it to the fixed <aside> root only when non-empty", async () => {
    const source = await read(FANCY_DRAWER);
    expect(source).toContain("view-transition-name: ${viewTransitionName.trim()}");
    const asideIndex = source.indexOf("<aside");
    const styleIndex = source.indexOf("style={rootStyle}");
    expect(styleIndex).toBeGreaterThan(asideIndex);
  });
});

describe("NavDrawer — the fixed rail is not exempt from the VT stacking contract", () => {
  test("carries its own optional viewTransitionName prop, defaulted empty", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toMatch(/viewTransitionName\s*=\s*""/);
  });

  test("the locked rail is fixed (not in-flow) and applies the name directly, unlike the source template's in-flow rail", async () => {
    const source = await read(NAV_DRAWER);
    // This template's rail is `fixed inset-y-0`, unlike the ported
    // reference's in-flow (`shrink-0`) rail — it is NOT exempt from the
    // VT-covering risk a fixed root carries, so it must set its own name.
    expect(source).toContain("fixed inset-y-0");
    expect(source).toContain("view-transition-name: ${viewTransitionName.trim()}");
  });

  test("forwards viewTransitionName to the FancyDrawer it composes for the unlocked presentation", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toMatch(/<FancyDrawer[\s\S]*?\{viewTransitionName\}/);
  });
});

describe("ChatDrawer — threads viewTransitionName onto the Drawer it composes", () => {
  test("carries its own optional viewTransitionName prop, defaulted empty", async () => {
    const source = await read(CHAT_DRAWER);
    expect(source).toMatch(/viewTransitionName\s*=\s*""/);
  });

  test("forwards it to overlay/Drawer", async () => {
    const source = await read(CHAT_DRAWER);
    expect(source).toMatch(/<Drawer[\s\S]*?\{viewTransitionName\}/);
  });
});

describe("Base.astro — the VT group name lives on the fixed root, never the island wrapper", () => {
  test("page-content carries the named page-main group", async () => {
    const source = await read(BASE_ASTRO);
    expect(source).toContain('transition:name="page-main"');
  });

  test("NavDrawer's persist id uses a distinct '-island' string from its VT group name (readability, not collision-avoidance — transition:persist creates no view-transition group to collide with)", async () => {
    const source = await read(BASE_ASTRO);
    expect(source).toContain('transition:persist="shell-nav-island"');
    expect(source).toContain('viewTransitionName="shell-nav"');
    expect("shell-nav-island").not.toBe("shell-nav");
  });

  test("ChatDrawer's persist id uses a distinct '-island' string from its VT group name (readability, not collision-avoidance)", async () => {
    const source = await read(BASE_ASTRO);
    expect(source).toContain('transition:persist="shell-chat-island"');
    expect(source).toContain('viewTransitionName="shell-chat"');
    expect("shell-chat-island").not.toBe("shell-chat");
  });

  test("neither transition:persist nor viewTransitionName is set on a wrapping Astro element — both ride the component props", async () => {
    const source = await read(BASE_ASTRO);
    // transition:persist/viewTransitionName appear as props on <NavDrawer>/
    // <ChatDrawer> themselves (the Astro island invocation), not on a <div>
    // wrapper around them.
    expect(source).not.toMatch(/<div[^>]*transition:persist/);
    expect(source).not.toMatch(/<div[^>]*viewTransitionName/);
  });
});

describe("app.css — every ::view-transition-group() name is actually assigned by the markup", () => {
  test("page-main is pinned low with no morph animation", async () => {
    const css = await read(APP_CSS);
    expect(css).toMatch(/::view-transition-group\(page-main\)\s*\{[^}]*animation:\s*none/);
  });

  test("shell-nav and shell-chat are stacked above page-main", async () => {
    const css = await read(APP_CSS);
    expect(css).toMatch(
      /::view-transition-group\(shell-nav\),\s*::view-transition-group\(shell-chat\)\s*\{[^}]*animation:\s*none/,
    );
  });

  test("no dead ::view-transition-group() name in the real app.css / Base.astro pair", async () => {
    const [css, base] = await Promise.all([read(APP_CSS), read(BASE_ASTRO)]);
    expect(findDeadGroupNames(css, base)).toEqual([]);
  });

  test("the literal group names live in Base.astro's props; NavDrawer/ChatDrawer carry only the plumbing", async () => {
    const [navDrawerSource, chatDrawerSource] = await Promise.all([
      read(NAV_DRAWER),
      read(CHAT_DRAWER),
    ]);
    // Never a hardcoded "shell-nav"/"shell-chat" of their own — that would
    // collide with the showcase gallery's second, unnamed NavDrawer
    // instance (both `<NavDrawer>`s render on `/showcase/components/` for a
    // role-holding session: Base.astro's real one, and the gallery's demo).
    expect(navDrawerSource).not.toContain('"shell-nav"');
    expect(chatDrawerSource).not.toContain('"shell-chat"');
  });
});

// --- The check itself, and proof it is not vacuous -------------------------
//
// This is the fix for the audited gap: a prior version of this file checked
// group names as bare substrings of Base.astro's source text, which passes
// identically whether or not a name is genuinely wired as a
// `view-transition-name` — exactly how `shell-nav-island` / `shell-chat-island`
// shipped as two dead CSS rules (removed from app.css) with matching
// `transition:persist="shell-*-island"` text that LOOKED like wiring but
// isn't: `transition:persist` sets only Astro's client-side DOM-identity
// attribute (`data-astro-transition-persist`) and emits no
// `$$renderTransition(...)` call and no `::view-transition-*` group at all.
// The two directives that DO create a live view-transition-name are
// `transition:name="X"` (Astro's own compiler-generated group) and this
// codebase's `viewTransitionName="X"` prop (threaded onto a fixed root's
// inline `style`, per overlay/Drawer.svelte, overlay/FancyDrawer.svelte,
// shell/NavDrawer.svelte, shell/ChatDrawer.svelte) — only those two count as
// "wired" below.

function extractGroupNames(css: string): string[] {
  const names = new Set<string>();
  for (const m of css.matchAll(/::view-transition-group\(([a-z0-9-]+)\)/g)) {
    names.add(m[1]!);
  }
  return [...names];
}

function extractWiredNames(astroSource: string): string[] {
  const names = new Set<string>();
  for (const m of astroSource.matchAll(/\btransition:name="([a-z0-9-]+)"/g)) names.add(m[1]!);
  for (const m of astroSource.matchAll(/\bviewTransitionName="([a-z0-9-]+)"/g)) names.add(m[1]!);
  return [...names];
}

/** Every CSS group name with no matching `transition:name`/`viewTransitionName`. */
function findDeadGroupNames(css: string, astroSource: string): string[] {
  const wired = new Set(extractWiredNames(astroSource));
  return extractGroupNames(css).filter((name) => !wired.has(name));
}

describe("findDeadGroupNames — the check that closes the audited gap, proven non-vacuous", () => {
  test("a name backed only by transition:persist is reported dead — reproduces the exact defect that shipped", () => {
    const astroSource = `<Island transition:persist="ghost-island" />`;
    const css = `::view-transition-group(ghost-island) { animation: none; }`;
    expect(findDeadGroupNames(css, astroSource)).toEqual(["ghost-island"]);
  });

  test("a name backed by transition:name is recognized as wired, not dead", () => {
    const astroSource = `<Main transition:name="bar-group" />`;
    const css = `::view-transition-group(bar-group) { animation: none; }`;
    expect(findDeadGroupNames(css, astroSource)).toEqual([]);
  });

  test("a name backed by the viewTransitionName prop is recognized as wired, not dead", () => {
    const astroSource = `<NavDrawer viewTransitionName="baz-group" />`;
    const css = `::view-transition-group(baz-group) { animation: none; }`;
    expect(findDeadGroupNames(css, astroSource)).toEqual([]);
  });

  test("a CSS rule with no matching directive at all is reported dead", () => {
    const astroSource = `<Nothing here="true" />`;
    const css = `::view-transition-group(nowhere) { animation: none; }`;
    expect(findDeadGroupNames(css, astroSource)).toEqual(["nowhere"]);
  });
});
