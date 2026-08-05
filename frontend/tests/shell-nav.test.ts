import { describe, expect, test } from "bun:test";
import path from "node:path";

// Source-level contract tests for the ported docked-rail/floating-drawer nav
// (bdd-12-navigation-shell). DOM-mount behavior (zero-props, no throw) is
// covered by component-mount.test.ts's self-discovering glob.

const ROOT = path.join(import.meta.dir, "..");
const NAV_TS = path.join(ROOT, "src", "lib", "components", "shell", "nav.ts");
const NAV_DRAWER = path.join(ROOT, "src", "lib", "components", "shell", "NavDrawer.svelte");
const NAV_ITEM = path.join(ROOT, "src", "lib", "components", "shell", "NavItem.svelte");
const NAV_LOCK_TOGGLE = path.join(ROOT, "src", "lib", "components", "shell", "NavLockToggle.svelte");
const FANCY_DRAWER = path.join(ROOT, "src", "lib", "components", "overlay", "FancyDrawer.svelte");

async function read(file: string): Promise<string> {
  return Bun.file(file).text();
}

describe("nav.ts — NAV_SECTIONS grouping capability", () => {
  test("NAV_SECTIONS wraps NAV_ITEMS with no invented content", async () => {
    const { NAV_ITEMS, NAV_SECTIONS } = await import(NAV_TS);
    expect(NAV_SECTIONS).toHaveLength(1);
    expect(NAV_SECTIONS[0].items).toBe(NAV_ITEMS);
    expect(NAV_SECTIONS[0].titleKey).toBeUndefined();
  });

  test("the template ships exactly the three existing routes", async () => {
    const { NAV_ITEMS } = await import(NAV_TS);
    const hrefs = NAV_ITEMS.map((item: { href: string }) => item.href);
    expect(hrefs).toEqual(["/chatui/", "/showcase/components/", "/profile/"]);
  });
});

describe("NavItem — tone prop for docked-rail contrast (adr-08 r9)", () => {
  test("defaults to 'default', so a bare mount needs no tone", async () => {
    const source = await read(NAV_ITEM);
    expect(source).toMatch(/tone\s*=\s*"default"/);
  });

  test("inverse tone drops the ghost hover fill for a no-panel rail", async () => {
    const source = await read(NAV_ITEM);
    expect(source).toMatch(/inverse\s*\?\s*"bare"\s*:\s*"ghost"/);
  });
});

describe("NavLockToggle — zero-prop safe, non-mutating by default (adr-23)", () => {
  test("onclick has no default handler — a bare click performs no action", async () => {
    const source = await read(NAV_LOCK_TOGGLE);
    expect(source).toMatch(/onclick\s*[,;:]/);
    expect(source).not.toContain("onclick = () =>");
  });

  test("locked defaults to false", async () => {
    const source = await read(NAV_LOCK_TOGGLE);
    expect(source).toMatch(/locked\s*=\s*false/);
  });
});

describe("FancyDrawer — hover-open floating panel, sibling of Drawer (adr-23 r2)", () => {
  test("carries the 2s leave cooldown", async () => {
    const source = await read(FANCY_DRAWER);
    expect(source).toContain("CLOSE_DELAY_MS = 2000");
  });

  test("dismisses on an outside pointerdown", async () => {
    const source = await read(FANCY_DRAWER);
    expect(source).toContain("onDocumentPointerDown");
  });

  test("open defaults to false, closed on a bare mount", async () => {
    const source = await read(FANCY_DRAWER);
    expect(source).toMatch(/open\s*=\s*\$bindable\(false\)/);
  });

  test("the peek tab is in-flow inside the aside's box, not absolute left-full (adr-28)", async () => {
    const source = await read(FANCY_DRAWER);
    expect(source).not.toContain("left-full");
    expect(source).not.toContain("right-full");
    expect(source).not.toContain("absolute top-1/2");
    expect(source).toContain("TAB_WIDTH");
  });

  test("the tab toggles on click, not only hover", async () => {
    const source = await read(FANCY_DRAWER);
    expect(source).toContain("onclick={onTabClick}");
  });
});

describe("NavDrawer — nav_lock cookie preference and non-mutating footer defaults", () => {
  test("preference comes from a prop (SSR), not from onMount/localStorage alone", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toMatch(/preference:\s*preferenceProp/);
    expect(source).not.toMatch(/localStorage\.getItem\(PIN_KEY\)/);
  });

  test("locking persists via writeNavLockCookie, not localStorage", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toContain("writeNavLockCookie(next)");
  });

  test("the legacy shell-nav-pinned key is migrated once, never written again", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toContain("migrateLegacyNavLock()");
    expect(source).not.toContain("localStorage.setItem");
  });

  test("the profile disc is inert unless navigates is set (adr-22 r2)", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toMatch(/href=\{navigates \? "\/profile\/" : "#"\}/);
  });

  test("the theme disc never PATCHes the backend — cookie-only, like QuickThemeToggle", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).not.toContain("fetch(");
    expect(source).not.toMatch(/PATCH\s*\//);
  });

  test("defaults to the unlocked (floating) mode", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toMatch(/preferenceProp\s*=\s*"unlocked"/);
  });

  test("carries no feedlot business content", async () => {
    const source = await read(NAV_DRAWER);
    const feedlotTerms = [
      "hacienda",
      "alimentacion",
      "sanidad",
      "pesajes",
      "racion",
      "gastos",
      "cow",
      "wheat",
      "OPERACIÓN",
      "NUTRICIÓN",
      "ADMINISTRACIÓN",
    ];
    for (const term of feedlotTerms) {
      expect(source.toLowerCase()).not.toContain(term.toLowerCase());
    }
  });
});
