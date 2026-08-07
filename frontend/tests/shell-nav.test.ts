import { describe, expect, test } from "bun:test";
import path from "node:path";
import { flushSync, mountAt, unmount } from "./component-mount.test";

// bun run test only — see component-mount.test.ts for why a bare `bun test`
// falsely fails this suite (no --conditions browser/svelte, no DOM). DOM-mount
// zero-prop coverage lives in component-mount.test.ts's self-discovering
// glob; this file pins load-bearing behavior the glob cannot parametrize.
// adr-28's preference x viewport render matrix is owned by a sibling file.

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

async function readCss(): Promise<string> {
  return Bun.file(APP_CSS).text();
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
  test("active state renders aria-current=page and a real accessible link", async () => {
    const { target, instance } = await mountAt(NAV_ITEM, {
      href: "/profile/",
      label: "Profile",
      active: true,
    });
    try {
      const link = target.querySelector("a") as HTMLAnchorElement;
      expect(link.getAttribute("aria-current")).toBe("page");
      expect(link.textContent).toContain("Profile");
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("inactive state carries no aria-current", async () => {
    const { target, instance } = await mountAt(NAV_ITEM, { href: "/profile/", label: "Profile" });
    try {
      const link = target.querySelector("a") as HTMLAnchorElement;
      expect(link.hasAttribute("aria-current")).toBe(false);
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});

describe("NavLockToggle — zero-prop safe, non-mutating by default (adr-23)", () => {
  test("a bare click performs no action", async () => {
    const { target, instance } = await mountAt(NAV_LOCK_TOGGLE);
    try {
      const button = target.querySelector("button") as HTMLButtonElement;
      expect(button.getAttribute("aria-pressed")).toBe("false");
      expect(() => button.click()).not.toThrow();
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("locked reflects into aria-pressed and fires the caller's onclick", async () => {
    let clicks = 0;
    const { target, instance } = await mountAt(NAV_LOCK_TOGGLE, {
      locked: true,
      onclick: () => clicks++,
    });
    try {
      const button = target.querySelector("button") as HTMLButtonElement;
      expect(button.getAttribute("aria-pressed")).toBe("true");
      button.click();
      expect(clicks).toBe(1);
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});

describe("FancyDrawer — hover-open floating panel, sibling of Drawer (adr-23 r2)", () => {
  test("opens on click and dismisses on an outside pointerdown", async () => {
    const { target, instance } = await mountAt(FANCY_DRAWER);
    try {
      const tab = target.querySelector("button") as HTMLButtonElement;
      tab.click();
      flushSync();
      expect(tab.getAttribute("aria-expanded")).toBe("true");

      document.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true }));
      flushSync();
      expect(tab.getAttribute("aria-expanded")).toBe("false");
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("closed by default on a bare mount", async () => {
    const { target, instance } = await mountAt(FANCY_DRAWER);
    try {
      const tab = target.querySelector("button") as HTMLButtonElement;
      expect(tab.getAttribute("aria-expanded")).toBe("false");
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});

describe("NavDrawer — nav_lock cookie preference and non-mutating footer defaults", () => {
  test("the profile disc is inert unless navigates is set (adr-22 r2)", async () => {
    const { target, instance } = await mountAt(NAV_DRAWER);
    try {
      const profileLink = [...target.querySelectorAll("a")].at(-1) as HTMLAnchorElement | undefined;
      expect(profileLink?.getAttribute("href")).toBe("#");
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("navigates=true wires the real profile href", async () => {
    const { target, instance } = await mountAt(NAV_DRAWER, { navigates: true });
    try {
      const profileLink = [...target.querySelectorAll("a")].find(
        (a) => a.getAttribute("href") === "/profile/",
      );
      expect(profileLink).toBeDefined();
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("the theme disc never issues a fetch on a bare mount", async () => {
    const nativeFetch = globalThis.fetch;
    let called = false;
    globalThis.fetch = (async (...args: Parameters<typeof fetch>) => {
      called = true;
      return nativeFetch(...args);
    }) as typeof fetch;
    const { target, instance } = await mountAt(NAV_DRAWER);
    try {
      expect(called).toBe(false);
    } finally {
      unmount(instance);
      target.remove();
      globalThis.fetch = nativeFetch;
    }
  });

  test("locked preference mounts a rail landmark", async () => {
    const { target, instance } = await mountAt(NAV_DRAWER, { preference: "locked" });
    try {
      expect(target.querySelector("aside")).not.toBeNull();
    } finally {
      unmount(instance);
      target.remove();
    }
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
    const css = await readCss();
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
  test("defaults to L via the data-drawer-size attribute", async () => {
    const { target, instance } = await mountAt(DRAWER);
    try {
      const aside = target.querySelector("aside") as HTMLElement;
      expect(aside.getAttribute("data-drawer-size")).toBe("L");
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("ChatDrawer defaults to XL (former 22rem chat width)", async () => {
    const { target, instance } = await mountAt(CHAT_DRAWER);
    try {
      const aside = target.querySelector("aside") as HTMLElement;
      expect(aside.getAttribute("data-drawer-size")).toBe("XL");
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});
