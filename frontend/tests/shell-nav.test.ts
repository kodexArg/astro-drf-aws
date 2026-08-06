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
const SHELL_SIZES = path.join(ROOT, "src", "lib", "components", "shell", "shell-sizes.ts");
const APP_CSS = path.join(ROOT, "src", "styles", "app.css");
const DRAWER = path.join(ROOT, "src", "lib", "components", "overlay", "Drawer.svelte");
const CHAT_DRAWER = path.join(ROOT, "src", "lib", "components", "shell", "ChatDrawer.svelte");
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
    // Capsule always uses bare; inverse paints a foreground wash, not ghost/secondary.
    expect(source).toContain('variant="bare"');
    expect(source).toContain("hover:bg-foreground/10");
    expect(source).not.toMatch(/variant=\{[^}]*"ghost"/);
  });

  test("icon sits in a bordered circular disc (feedlot capsule)", async () => {
    const source = await read(NAV_ITEM);
    expect(source).toContain("rounded-full border");
    expect(source).toContain("size-8 shrink-0 place-items-center");
    expect(source).toContain("border-primary bg-primary text-primary-foreground");
  });

  test("dense mode tightens gap/padding for asideSize S", async () => {
    const source = await read(NAV_ITEM);
    expect(source).toMatch(/dense\s*=\s*false/);
    expect(source).toContain('dense ? "gap-1.5 pr-2" : "gap-2 pr-3"');
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

  test("asideSize defaults to M and drives width via shell tokens", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toMatch(/asideSize\s*=\s*"M"/);
    expect(source).toContain("ASIDE_SIZE_VAR[asideSize]");
    expect(source).not.toContain('const RAIL_WIDTH = "14rem"');
  });

  test("locked rail is viewport-fixed (h-dvh), not page-tall self-stretch", async () => {
    const source = await read(NAV_DRAWER);
    expect(source).toContain("data-aside-spacer");
    expect(source).toContain("fixed inset-y-0");
    expect(source).toContain("h-dvh");
    expect(source).not.toMatch(/"flex[^"]*self-stretch/);
  });
});

describe("shell-sizes — aside L/M/S and drawer XL/L/M/S tokens", () => {
  test("aside M and drawer M resolve to the same CSS variable chain", async () => {
    const { ASIDE_SIZE_VAR, DRAWER_SIZE_VAR } = await import(SHELL_SIZES);
    expect(ASIDE_SIZE_VAR.M).toBe("var(--shell-aside-m)");
    expect(DRAWER_SIZE_VAR.M).toBe("var(--shell-drawer-m)");
    expect(DRAWER_SIZE_VAR.S).toBe("var(--shell-drawer-s)");
    expect(ASIDE_SIZE_VAR.S).toBe("var(--shell-aside-s)");
  });

  test("app.css pins rem values and aliases drawer M/S to aside M/S", async () => {
    const css = await read(APP_CSS);
    expect(css).toContain("--shell-aside-l: 15rem");
    expect(css).toContain("--shell-aside-m: 11rem");
    expect(css).toContain("--shell-aside-s: 9rem");
    expect(css).toContain("--shell-drawer-xl: 22rem");
    expect(css).toContain("--shell-drawer-l: 18rem");
    expect(css).toContain("--shell-drawer-m: var(--shell-aside-m)");
    expect(css).toContain("--shell-drawer-s: var(--shell-aside-s)");
  });
});

describe("Drawer — size enum XL|L|M|S default L", () => {
  test("defaults to L and no longer takes a freeform width prop", async () => {
    const source = await read(DRAWER);
    expect(source).toMatch(/size\s*=\s*"L"/);
    expect(source).toContain("DRAWER_SIZE_VAR[size]");
    expect(source).not.toMatch(/width\s*=\s*"18rem"/);
  });

  test("ChatDrawer defaults to XL (former 22rem chat width)", async () => {
    const source = await read(CHAT_DRAWER);
    expect(source).toMatch(/size\s*=\s*"XL"/);
    expect(source).toContain("{size}");
    expect(source).not.toContain('width="22rem"');
  });
});
