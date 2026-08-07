import { describe, expect, test } from "bun:test";
import path from "node:path";
import {
  DESK_MIN_WIDTH,
  RAIL_MIN_WIDTH,
  resolvePresentation,
  type NavLockPreference,
  type NavViewport,
} from "../src/lib/components/shell/nav-fsm";

// adr-28 rule 3: the menu is never invisible. nav-fsm.test.ts proves the pure
// matrix and shell-nav.test.ts greps the source; this mounts the real
// component across preference x viewport and reads the DOM it produces.
//
// happy-dom has no CSS/media-query engine, so the rail-vs-drawer CSS
// visibility split at RAIL_MIN_WIDTH cannot be read via getComputedStyle
// (same limit documented in component-mount.test.ts's SessionBadge popover
// test). The honest, DOM-real anchor instead: the component always mounts
// BOTH candidates for locked preference (CSS arbitrates which one shows),
// their wrapper classes cite the FSM's own breakpoint constants (so a
// literal drift between the class and the constant fails here), and the
// mocked matchMedia wiring drives the real internal viewport state through
// to the rendered NavLockToggle prop — a genuine behavioral assertion.

if (typeof document === "undefined") {
  const { GlobalRegistrator } = await import("@happy-dom/global-registrator");
  const nativeHttp = {
    fetch: globalThis.fetch,
    Request: globalThis.Request,
    Response: globalThis.Response,
    Headers: globalThis.Headers,
  };
  GlobalRegistrator.register();
  Object.assign(globalThis, nativeHttp);
}

const g = globalThis as { __svelteBunPluginInstalled?: boolean };
if (!g.__svelteBunPluginInstalled) {
  g.__svelteBunPluginInstalled = true;
  const { compile } = await import("svelte/compiler");
  Bun.plugin({
    name: "svelte-nav-render-matrix",
    setup(build) {
      build.onLoad({ filter: /\.svelte$/ }, async ({ path: file }) => {
        const source = await Bun.file(file).text();
        const { js } = compile(source, { filename: file, generate: "client", css: "injected" });
        return { contents: js.code, loader: "js" };
      });
    },
  });
}

const { mount, unmount, flushSync } = await import("svelte");
const NavDrawer = (await import("../src/lib/components/shell/NavDrawer.svelte")).default;

const RAIL_PX = parseFloat(RAIL_MIN_WIDTH) * 16;
const DESK_PX = parseFloat(DESK_MIN_WIDTH) * 16;

function widthFor(viewport: NavViewport): number {
  if (viewport === "mobile") return RAIL_PX - 1;
  if (viewport === "tablet") return DESK_PX - 1;
  return DESK_PX + 1;
}

/** Stubs matchMedia against a fixed width, mirroring the component's own
 * `resolveViewport(railFits, deskFits)` wiring — real behavioral coupling,
 * not a duplicated constant. */
function stubMatchMedia(width: number): () => void {
  const original = window.matchMedia;
  window.matchMedia = ((query: string) => {
    const match = query.match(/min-width:\s*([\d.]+)rem/);
    const thresholdPx = match ? parseFloat(match[1]) * 16 : 0;
    return {
      matches: width >= thresholdPx,
      media: query,
      addEventListener() {},
      removeEventListener() {},
    } as MediaQueryList;
  }) as typeof window.matchMedia;
  return () => {
    window.matchMedia = original;
  };
}

function renderNav(preference: NavLockPreference, viewport: NavViewport) {
  const restore = stubMatchMedia(widthFor(viewport));
  const target = document.createElement("div");
  document.body.appendChild(target);
  const instance = mount(NavDrawer, { target, props: { preference } });
  flushSync();
  return {
    target,
    cleanup() {
      unmount(instance);
      target.remove();
      restore();
    },
  };
}

describe("adr-28 rule 3 — NavDrawer never renders invisible across the matrix", () => {
  const preferences: NavLockPreference[] = ["locked", "unlocked"];
  const viewports: NavViewport[] = ["mobile", "tablet", "desk"];

  for (const preference of preferences) {
    for (const viewport of viewports) {
      test(`preference=${preference} viewport=${viewport} renders an operable caret or rail`, () => {
        const { target, cleanup } = renderNav(preference, viewport);
        try {
          const caret = target.querySelector("aside button[aria-expanded]");
          expect(caret).not.toBeNull();
          expect(caret!.hasAttribute("disabled")).toBe(false);
          expect(caret!.getAttribute("aria-hidden")).not.toBe("true");

          if (preference === "locked") {
            const rail = target.querySelector("aside[data-aside-size]");
            expect(rail).not.toBeNull();
            const spacer = target.querySelector("[data-aside-spacer]");
            expect(spacer).not.toBeNull();

            const railWrapper = spacer!.parentElement!;
            const drawerAside = caret!.closest("aside")!;
            const drawerWrapper = drawerAside.parentElement!;
            // The two wrappers must cite the SAME breakpoint the FSM uses,
            // never a locally re-typed literal.
            const bp = RAIL_MIN_WIDTH.replace(".", "\\.");
            expect(railWrapper.className).toMatch(new RegExp(`min-\\[${bp}\\]`));
            expect(drawerWrapper.className).toMatch(new RegExp(`min-\\[${bp}\\]`));
            expect(railWrapper.className).not.toBe(drawerWrapper.className);
          }
        } finally {
          cleanup();
        }
      });
    }
  }

  test("locked mode reflects the resolved presentation onto NavLockToggle (real matchMedia wiring)", () => {
    for (const viewport of ["mobile", "tablet", "desk"] as NavViewport[]) {
      const { target, cleanup } = renderNav("locked", viewport);
      try {
        const toggle = target.querySelector('button[aria-pressed]');
        expect(toggle).not.toBeNull();
        const expectedLocked = resolvePresentation("locked", viewport) === "rail";
        expect(toggle!.getAttribute("aria-pressed")).toBe(String(expectedLocked));
      } finally {
        cleanup();
      }
    }
  });
});

describe("adr-28 rule 4 — the collapsed peek caret stays inside the transformed element's hit box", () => {
  test("the caret button is a DOM descendant of the transformed <aside>, not portaled out", () => {
    const { target, cleanup } = renderNav("unlocked", "desk");
    try {
      const asideEl = target.querySelector("aside")!;
      const caret = asideEl.querySelector("button[aria-expanded]");
      expect(caret).not.toBeNull();
      expect(asideEl.contains(caret)).toBe(true);

      const style = asideEl.getAttribute("style") ?? "";
      expect(style).toContain("transform:");

      // The regression this guards (issue behind shell-nav.test.ts's
      // left-full/right-full check): the caret positioned OUTSIDE the
      // translated box via its own absolute placement.
      const caretClass = caret!.getAttribute("class") ?? "";
      expect(caretClass).not.toMatch(/\bleft-full\b|\bright-full\b/);
    } finally {
      cleanup();
    }
  });
});
