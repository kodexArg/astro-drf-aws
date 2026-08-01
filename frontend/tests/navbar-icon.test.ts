import { describe, expect, test } from "bun:test";
import path from "node:path";

// NavbarIcon's component contract, ported from the gateway's
// navbar-icon.test.ts — its bdd-30 `data-amounts` half (the treasury amount
// abbreviation feature) does not exist in this template and is deliberately
// dropped. What remains is source-level by necessity: the assertions are
// about defaults and attribute wiring a DOM-free test cannot observe at
// runtime.

const ROOT = path.join(import.meta.dir, "..");
const NAVBAR_ICON = path.join(ROOT, "src", "lib", "components", "shell", "NavbarIcon.svelte");
const APP_CSS = path.join(ROOT, "src", "styles", "app.css");

async function read(file: string): Promise<string> {
  return Bun.file(file).text();
}

describe("NavbarIcon — the component contract", () => {
  test("every prop has a default, so a bare mount is valid (adr-22 r1)", async () => {
    const source = await read(NAVBAR_ICON);
    expect(source).toMatch(/icon\s*=\s*undefined/);
    expect(source).toMatch(/label\s*=\s*""/);
    expect(source).toMatch(/active\s*=\s*false/);
    expect(source).toMatch(/onclick\s*=\s*undefined/);
  });

  test("the click handler is optional-called, never assumed (adr-22 r2)", async () => {
    // A bare `onclick()` would throw on the zero-prop mount.
    const source = await read(NAVBAR_ICON);
    expect(source).toContain("onclick?.()");
  });

  test("it always has an accessible name, even with no label", async () => {
    const source = await read(NAVBAR_ICON);
    expect(source).toMatch(/label\s*\|\|\s*t\("navbar_icon_fallback"\)/);
    expect(source).toContain("aria-label={accessibleName}");
  });

  test("state is announced, not just painted", async () => {
    const source = await read(NAVBAR_ICON);
    expect(source).toContain("aria-pressed={active}");
  });

  test("the active colour comes from the token, never a literal", async () => {
    const source = await read(NAVBAR_ICON);
    expect(source).toContain("text-accent-active");
    expect(source).not.toMatch(/oklch\(|#[0-9a-fA-F]{3,8}/);
  });

  test("it carries a visible focus ring", async () => {
    const source = await read(NAVBAR_ICON);
    expect(source).toContain("focus-visible:ring-ring");
  });

  test("hovering an active icon does not blank its active colour", async () => {
    // Caught live in the browser, by no other gate: hover variants outrank base
    // utilities, so the accent vanished while the pointer rested on the control.
    const source = await read(NAVBAR_ICON);
    expect(source).toContain("hover:text-accent-active");
    // The unconditional form is the defect; the colour may only change on
    // hover in the INACTIVE branch.
    expect(source).not.toMatch(/"hover:bg-accent hover:text-accent-foreground"/);
  });

  test("hover restyles the surface, which is state-independent", async () => {
    const source = await read(NAVBAR_ICON);
    expect(source).toContain("hover:bg-accent");
  });
});

describe("NavbarIcon — the --accent-active token ships a light/dark pair", () => {
  // A light-only token renders muddy or invisible in dark mode ([[DESIGN-SYSTEM]]).
  test("declared in :root and again under .dark", async () => {
    const css = await read(APP_CSS);
    const declarations = css.match(/^\s*--accent-active:/gm) ?? [];
    expect(declarations).toHaveLength(2);
  });

  test("the dark value is lighter than the light one", async () => {
    const css = await read(APP_CSS);
    const values = [...css.matchAll(/--accent-active:\s*oklch\(([0-9.]+)/g)].map((m) =>
      Number(m[1]),
    );
    expect(values).toHaveLength(2);
    const [light, dark] = values;
    expect(dark).toBeGreaterThan(light);
  });

  test("it is exposed to Tailwind as a utility colour", async () => {
    const css = await read(APP_CSS);
    expect(css).toContain("--color-accent-active: var(--accent-active);");
  });

  test("it is not merely an alias of --accent or --primary", async () => {
    const css = await read(APP_CSS);
    expect(css).not.toMatch(/--accent-active:\s*var\(--(accent|primary)\)/);
  });
});
