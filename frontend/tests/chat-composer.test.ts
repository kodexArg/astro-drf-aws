import { describe, expect, test } from "bun:test";
import path from "node:path";
import { flushSync, mountAt, unmount } from "./component-mount.test";

// bun run test only — see component-mount.test.ts for why a bare `bun test`
// falsely fails this suite (no --conditions browser/svelte, no DOM).

const ROOT = path.join(import.meta.dir, "..");
const COMPOSER = path.join(ROOT, "src", "lib", "components", "chat", "ChatComposer.svelte");
const CHAT_DRAWER = path.join(ROOT, "src", "lib", "components", "shell", "ChatDrawer.svelte");

function type(textarea: HTMLTextAreaElement, text: string): void {
  textarea.value = text;
  textarea.dispatchEvent(new Event("input", { bubbles: true }));
  flushSync();
}

function press(
  textarea: HTMLTextAreaElement,
  key: string,
  opts: { shiftKey?: boolean; isComposing?: boolean } = {},
): void {
  const event = new KeyboardEvent("keydown", { key, shiftKey: opts.shiftKey, cancelable: true, bubbles: true });
  if (opts.isComposing) Object.defineProperty(event, "isComposing", { value: true });
  textarea.dispatchEvent(event);
  flushSync();
}

describe("ChatComposer — Enter sends, Shift+Enter and IME composition do not", () => {
  test("Enter submits the trimmed text and clears the field", async () => {
    const submitted: string[] = [];
    const { target, instance } = await mountAt(COMPOSER, {
      ariaLabel: "message",
      sendLabel: "send",
      onsubmit: (text: string) => submitted.push(text),
    });
    try {
      const textarea = target.querySelector("textarea") as HTMLTextAreaElement;
      type(textarea, "hello");
      press(textarea, "Enter");

      expect(submitted).toEqual(["hello"]);
      expect(textarea.value).toBe("");
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("Shift+Enter does not submit", async () => {
    const submitted: string[] = [];
    const { target, instance } = await mountAt(COMPOSER, {
      ariaLabel: "message",
      sendLabel: "send",
      onsubmit: (text: string) => submitted.push(text),
    });
    try {
      const textarea = target.querySelector("textarea") as HTMLTextAreaElement;
      type(textarea, "hello");
      press(textarea, "Enter", { shiftKey: true });

      expect(submitted).toEqual([]);
      expect(textarea.value).toBe("hello");
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("Enter during IME composition does not submit", async () => {
    const submitted: string[] = [];
    const { target, instance } = await mountAt(COMPOSER, {
      ariaLabel: "message",
      sendLabel: "send",
      onsubmit: (text: string) => submitted.push(text),
    });
    try {
      const textarea = target.querySelector("textarea") as HTMLTextAreaElement;
      type(textarea, "hello");
      press(textarea, "Enter", { isComposing: true });

      expect(submitted).toEqual([]);
    } finally {
      unmount(instance);
      target.remove();
    }
  });

  test("the send button submits and is disabled while empty", async () => {
    const submitted: string[] = [];
    const { target, instance } = await mountAt(COMPOSER, {
      ariaLabel: "message",
      sendLabel: "send",
      onsubmit: (text: string) => submitted.push(text),
    });
    try {
      const button = target.querySelector("button") as HTMLButtonElement;
      expect(button.disabled).toBe(true);

      const textarea = target.querySelector("textarea") as HTMLTextAreaElement;
      type(textarea, "hi");
      expect(button.disabled).toBe(false);

      button.click();
      expect(submitted).toEqual(["hi"]);
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});

describe("ChatDrawer — the peek control renders a literal ? for the assistant surface", () => {
  test("peekIcon renders the ? glyph", async () => {
    const { target, instance } = await mountAt(CHAT_DRAWER);
    try {
      const peek = target.querySelector("button[aria-expanded]") as HTMLButtonElement;
      expect(peek.textContent?.trim()).toBe("?");
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});
