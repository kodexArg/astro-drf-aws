import { describe, expect, test } from "bun:test";
import path from "node:path";
import { flushSync, mountAt, unmount } from "./component-mount.test";

// bun run test only — see component-mount.test.ts for why a bare `bun test`
// falsely fails this suite (no --conditions browser/svelte, no DOM).

const CONTEXT_MENU = path.join(
  import.meta.dir,
  "..",
  "src",
  "lib",
  "components",
  "nav",
  "ContextMenu.svelte",
);

describe("ContextMenu — outside dismiss without Melt trigger", () => {
  test("opens on right-click and closes on a pointerdown outside the content", async () => {
    const { target, instance } = await mountAt(CONTEXT_MENU);
    try {
      const region = target.querySelector("div") as HTMLElement;
      region.dispatchEvent(
        new MouseEvent("contextmenu", { bubbles: true, cancelable: true, clientX: 10, clientY: 10 }),
      );
      flushSync();

      const content = target.querySelector('[role="menu"]') as HTMLElement;
      expect(content).not.toBeNull();
      expect(content.getAttribute("data-open")).toBe("");
      expect(content.getAttribute("inert")).toBeNull();

      document.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true }));
      flushSync();

      expect(content.getAttribute("data-open")).toBeNull();
      expect(content.hasAttribute("inert")).toBe(true);
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});
