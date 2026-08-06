import { describe, expect, test } from "bun:test";
import { readFile } from "node:fs/promises";
import path from "node:path";

const ROOT = path.join(import.meta.dir, "..");
const COMPOSER = path.join(ROOT, "src", "lib", "components", "chat", "ChatComposer.svelte");
const CHAT_UI = path.join(ROOT, "src", "lib", "components", "chat", "ChatUI.svelte");
const CHAT_DRAWER = path.join(ROOT, "src", "lib", "components", "shell", "ChatDrawer.svelte");
const DRAWER = path.join(ROOT, "src", "lib", "components", "overlay", "Drawer.svelte");

async function read(file: string): Promise<string> {
  return readFile(file, "utf8");
}

describe("ChatComposer — icon-only multiline contracts", () => {
  test("uses a textarea (not Input) with resize-none and flex width", async () => {
    const source = await read(COMPOSER);
    expect(source).toContain("<textarea");
    expect(source).toContain("resize-none");
    expect(source).toContain("min-w-0 flex-1");
    expect(source).toContain("max-h-28");
    expect(source).toContain("overflow-y-auto");
    expect(source).not.toContain("field-sizing-content");
    expect(source).not.toMatch(/from "\$lib\/components\/ui\/input"/);
  });

  test("autosizes via scrollHeight + border-y (border-box); no manual resize handle", async () => {
    const source = await read(COMPOSER);
    expect(source).toContain("function autoresize");
    expect(source).toContain("scrollHeight");
    expect(source).toContain("borderTopWidth");
    expect(source).toContain("borderBottomWidth");
    expect(source).toContain("oninput={autoresize}");
    expect(source).toContain("resize-none");
    expect(source).toContain("box-border");
    // Collapse to 0 before measure so UA/rows intrinsic cannot inflate single-line.
    expect(source).toContain('el.style.height = "0px"');
  });

  test("single-line field is padding-driven (py-2 + leading-5); no locked button height", async () => {
    const source = await read(COMPOSER);
    // Resting height is py-2 + leading-5 + border (RESTING_H_PX), not a fixed utility.
    expect(source).toContain("RESTING_H_PX");
    expect(source).toContain("min-h-0");
    expect(source).toContain("py-2");
    expect(source).toContain("leading-5");
    expect(source).not.toContain("min-h-9");
    // Pin resting/grown height inline — never clear to "" (UA/rows would inflate).
    expect(source).toContain("`${RESTING_H_PX}px`");
    expect(source).not.toContain('el.style.height = ""');
    // Field classes: py-2, no h-9 lock, no magic 7px pad, no shadow/sunken.
    const fieldClassMatch = source.match(/const fieldClass =\s*\n?\s*"([^"]+)"/);
    const fieldClass = fieldClassMatch?.[1] ?? "";
    expect(fieldClass).toContain("py-2");
    expect(fieldClass).not.toMatch(/\bh-9\b/);
    expect(fieldClass).not.toMatch(/py-\[7px\]/);
    expect(fieldClass).not.toMatch(/\bshadow(?:-sm)?\b/);
    expect(source).not.toContain("sunken");
  });

  test("send control is icon-only with accessible label, no visible Enviar text", async () => {
    const source = await read(COMPOSER);
    expect(source).toContain('size="icon"');
    expect(source).toContain("aria-label={sendLabel}");
    expect(source).toContain("<Send");
    // Visible sendLabel must not render as button children (icon-only).
    expect(source).not.toMatch(/<\/Send>\s*\{sendLabel\}/);
    expect(source).not.toMatch(/>\s*\{sendLabel\}\s*</);
  });

  test("Enter sends; Shift+Enter and IME composition do not", async () => {
    const source = await read(COMPOSER);
    expect(source).toContain("e.shiftKey");
    expect(source).toContain("e.isComposing");
    expect(source).toMatch(/e\.key !== "Enter"/);
    expect(source).toContain("e.preventDefault()");
    expect(source).toContain("submit()");
  });

  test("row centers on single-line; button self-end only when tall", async () => {
    const source = await read(COMPOSER);
    // Flush top/bottom when both are near h-9; grow textarea only, pin button when multiline.
    expect(source).toContain("items-center");
    expect(source).toContain("self-end");
    expect(source).toContain("tall");
    expect(source).not.toMatch(/flex min-w-0 w-full items-end/);
  });

  test("typewriter overlay flex-centers (no py fake-match to textarea pad)", async () => {
    const source = await read(COMPOSER);
    expect(source).toContain("showTypewriter");
    expect(source).toMatch(
      /absolute inset-0 flex items-center[^"]*px-3[^"]*leading-5/,
    );
    const overlayMatch = source.match(/const overlayClass =\s*\n?\s*"([^"]+)"/);
    expect(overlayMatch?.[1] ?? "").not.toMatch(/py-/);
    expect(source).not.toMatch(/absolute inset-x-3 top-0 flex h-9 items-center/);
  });
});

describe("Chat drawer chrome — height chain + peek ?", () => {
  test("Drawer panel fills the fixed aside (h-full min-h-0)", async () => {
    const source = await read(DRAWER);
    expect(source).toContain("h-full min-h-0");
  });

  test("ChatDrawer peek is a literal ? and ChatUI fills height", async () => {
    const source = await read(CHAT_DRAWER);
    expect(source).toContain("peekIcon");
    expect(source).toMatch(/>\?</);
    expect(source).toContain("overflow-hidden");
    expect(source).toContain("h-full min-h-0 flex-1");
  });

  test("ChatUI docks composer with h-full flex column", async () => {
    const source = await read(CHAT_UI);
    expect(source).toContain("h-full min-h-0");
    expect(source).toContain("shrink-0");
    expect(source).toContain("ChatComposer");
  });
});
