import { describe, expect, test } from "bun:test";

// adr-25 rules 3-4: the request carries a page IDENTITY, never scraped page
// text, and the rendered answer never mints a link out of free prose — only
// the structured `links` array produces a real anchor.

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
    name: "svelte-assistant-boundary",
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
const ChatUI = (await import("../src/lib/components/chat/ChatUI.svelte")).default;
const ChatMessageList = (await import("../src/lib/components/chat/ChatMessageList.svelte"))
  .default;

const nativeFetch = globalThis.fetch;

async function submitViaComposer(target: HTMLElement, text: string): Promise<void> {
  const textarea = target.querySelector("textarea")!;
  textarea.value = text;
  textarea.dispatchEvent(new Event("input", { bubbles: true }));
  flushSync();
  textarea.dispatchEvent(
    new KeyboardEvent("keydown", { key: "Enter", bubbles: true, cancelable: true }),
  );
  flushSync();
  await Promise.resolve();
}

describe("adr-25 rule 3 — the assistant request carries an identity, never scraped text", () => {
  test("POST body is exactly {utterance, page}, page is the caller's prop, not DOM content", async () => {
    // Real, unrelated page content that a naive scrape would have leaked.
    document.title = "SECRET-PAGE-CONTENT";
    const decoy = document.createElement("div");
    decoy.textContent = "SECRET-PAGE-CONTENT unrelated dom text";
    document.body.appendChild(decoy);

    let capturedBody = "";
    globalThis.fetch = (async (_url: string, init?: RequestInit) => {
      capturedBody = init?.body as string;
      return new Response(JSON.stringify({ answer: "ok", links: [], query_id: 1 }));
    }) as typeof fetch;

    const target = document.createElement("div");
    document.body.appendChild(target);
    const instance = mount(ChatUI, {
      target,
      props: {
        mode: "assistant",
        page: "/holding/",
        publicBackendUrl: "http://backend",
        copy: {
          title: "",
          composerPlaceholder: "",
          composerAriaLabel: "ask",
          composerSend: "send",
          messageGo: "go",
          messageConfirm: "confirm",
          outcomeCopy: {},
        },
      },
    });
    flushSync();

    try {
      await submitViaComposer(target, "hola");

      const parsed = JSON.parse(capturedBody);
      expect(Object.keys(parsed).sort()).toEqual(["page", "utterance"]);
      expect(parsed.page).toBe("/holding/");
      expect(parsed.utterance).toBe("hola");
      expect(capturedBody).not.toContain("SECRET-PAGE-CONTENT");
    } finally {
      unmount(instance);
      target.remove();
      decoy.remove();
      globalThis.fetch = nativeFetch;
    }
  });
});

describe("adr-25 rule 4 — prose never mints a link; only structured links render an anchor", () => {
  test("a URL embedded in free text produces no <a>; only the links array does", () => {
    const target = document.createElement("div");
    document.body.appendChild(target);

    const instance = mount(ChatMessageList, {
      target,
      props: {
        copy: { go: "go", confirm: "confirm" },
        messages: [
          {
            id: "1",
            role: "assistant",
            text: "Ver https://evil.example/attack o [click me](/holding/) para info",
            links: [{ target: "/holding/", label: "Holding" }],
          },
        ],
      },
    });
    flushSync();

    try {
      const anchors = target.querySelectorAll("a");
      expect(anchors.length).toBe(1);
      expect(anchors[0]!.getAttribute("href")).toBe("/holding/");
      expect(anchors[0]!.textContent).toBe("Holding");

      // The raw URL/markdown syntax survived as inert text, never linkified.
      const bubble = target.textContent ?? "";
      expect(bubble).toContain("https://evil.example/attack");
      expect(bubble).toContain("[click me](/holding/)");
    } finally {
      unmount(instance);
      target.remove();
    }
  });
});
