import { describe, expect, test } from "bun:test";
import path from "node:path";
import { mountAt, unmount } from "./component-mount.test";

// bun run test only — see component-mount.test.ts for why a bare `bun test`
// falsely fails this suite (no --conditions browser/svelte, no DOM).

const ROOT = path.join(import.meta.dir, "..");
const NAVBAR_ICON = path.join(ROOT, "src", "lib", "components", "shell", "NavbarIcon.svelte");
const APP_CSS = path.join(ROOT, "src", "styles", "app.css");

async function readCss(): Promise<string> {
  return Bun.file(APP_CSS).text();
}

describe("NavbarIcon — the component contract", () => {
  test("a bare mount renders an accessible button with a fallback label", async () => {
    const { target, instance } = await mountAt(NAVBAR_ICON);
    try {
      const button = target.querySelector("button") as HTMLButtonElement;
      expect(button).not.toBeNull();
      expect(button.getAttribute("aria-label")).not.toBe("");
      expect(button.getAttribute("aria-pressed")).toBe("false");
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("a bare click performs no action (onclick defaults to a no-op)", async () => {
    const { target, instance } = await mountAt(NAVBAR_ICON);
    try {
      const button = target.querySelector("button") as HTMLButtonElement;
      expect(() => button.click()).not.toThrow();
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("announces state via aria-pressed and a real label", async () => {
    const active = await mountAt(NAVBAR_ICON, { label: "Home", active: true });
    try {
      const button = active.target.querySelector("button") as HTMLButtonElement;
      expect(button.getAttribute("aria-pressed")).toBe("true");
      expect(button.getAttribute("aria-label")).toBe("Home");
    } finally {
      unmount(active.instance);
      active.target.remove();
    }

    const inactive = await mountAt(NAVBAR_ICON, { label: "Home", active: false });
    try {
      const button = inactive.target.querySelector("button") as HTMLButtonElement;
      expect(button.getAttribute("aria-pressed")).toBe("false");
    } finally {
      unmount(inactive.instance);
      inactive.target.remove();
    }
  });

  test("onclick fires the caller-supplied callback exactly once per click", async () => {
    let calls = 0;
    const { target, instance } = await mountAt(NAVBAR_ICON, { onclick: () => calls++ });
    try {
      const button = target.querySelector("button") as HTMLButtonElement;
      button.click();
      button.click();
      expect(calls).toBe(2);
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});

// happy-dom does not implement cascade order / computed style resolution, so
// the hover-vs-active cascade regression this component's history guards
// against is not reachable from this harness — only class-token presence is,
// asserted here as an honest, narrower substitute, never as a cascade proof.
describe("NavbarIcon — active colour class wiring (honest limit: not a cascade proof)", () => {
  test("active state carries the accent-active class, never a literal colour", async () => {
    const { target, instance } = await mountAt(NAVBAR_ICON, { active: true });
    try {
      const button = target.querySelector("button") as HTMLButtonElement;
      const classList = button.getAttribute("class") ?? "";
      expect(classList).toContain("text-accent-active");
      expect(classList).not.toMatch(/oklch\(|#[0-9a-fA-F]{3,8}/);
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});

describe("NavbarIcon — the --accent-active token ships a light/dark pair", () => {
  test("declared in :root and again under .dark", async () => {
    const css = await readCss();
    const declarations = css.match(/^\s*--accent-active:/gm) ?? [];
    expect(declarations).toHaveLength(2);
  });

  test("the dark value is lighter than the light one", async () => {
    const css = await readCss();
    const values = [...css.matchAll(/--accent-active:\s*oklch\(([0-9.]+)/g)].map((m) =>
      Number(m[1]),
    );
    expect(values).toHaveLength(2);
    const [light, dark] = values;
    expect(dark).toBeGreaterThan(light);
  });

  test("it is exposed to Tailwind as a utility colour", async () => {
    const css = await readCss();
    expect(css).toContain("--color-accent-active: var(--accent-active);");
  });

  test("it is not merely an alias of --accent or --primary", async () => {
    const css = await readCss();
    expect(css).not.toMatch(/--accent-active:\s*var\(--(accent|primary)\)/);
  });
});
