import { describe, expect, test } from "bun:test";
import {
  askAssistant,
  statusKeyForAskResult,
  type FetchLike,
} from "../src/lib/assistant-client";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("askAssistant", () => {
  test("POSTs to /api/assistant/ask/ with utterance and page", async () => {
    let capturedUrl = "";
    let capturedInit: RequestInit | undefined;
    const fetchImpl: FetchLike = async (url, init) => {
      capturedUrl = url;
      capturedInit = init;
      return jsonResponse({ answer: "Hola", links: [], query_id: 1 });
    };

    await askAssistant("http://localhost:8000", "¿saldo?", "/holding/", "csrf-1", fetchImpl);

    expect(capturedUrl).toBe("http://localhost:8000/api/assistant/ask/");
    expect(capturedInit?.method).toBe("POST");
    expect(capturedInit?.credentials).toBe("include");
    const headers = capturedInit?.headers as Record<string, string>;
    expect(headers["X-CSRFToken"]).toBe("csrf-1");
    expect(JSON.parse(capturedInit?.body as string)).toEqual({
      utterance: "¿saldo?",
      page: "/holding/",
    });
  });

  test("answer outcome keeps free text and structured links", async () => {
    const fetchImpl: FetchLike = async () =>
      jsonResponse({
        answer: "Disponible $1.2k",
        links: [{ target: "/holding/", label: "Holding" }],
        query_id: 9,
      });
    const result = await askAssistant("http://b", "q", "/holding/", "c", fetchImpl);
    expect(result).toEqual({
      kind: "answer",
      data: {
        answer: "Disponible $1.2k",
        links: [{ target: "/holding/", label: "Holding" }],
        query_id: 9,
      },
    });
  });

  test("disabled, 429, 503, 400 map to closed kinds", async () => {
    const disabled: FetchLike = async () =>
      jsonResponse({ outcome: "disabled", query_id: 1 });
    expect((await askAssistant("http://b", "q", "/", "c", disabled)).kind).toBe("disabled");

    const throttled: FetchLike = async () => new Response(null, { status: 429 });
    expect((await askAssistant("http://b", "q", "/", "c", throttled)).kind).toBe("throttled");

    const unavailable: FetchLike = async () =>
      jsonResponse({ detail: "assistant_unavailable" }, 503);
    expect((await askAssistant("http://b", "q", "/", "c", unavailable)).kind).toBe(
      "unavailable",
    );

    const bad: FetchLike = async () => jsonResponse({ page: ["invalid"] }, 400);
    expect((await askAssistant("http://b", "q", "/x/", "c", bad)).kind).toBe(
      "validation_error",
    );
  });

  test("statusKeyForAskResult never invents free prose", () => {
    expect(statusKeyForAskResult({ kind: "throttled" })).toBe("assistant_outcome_throttled");
    expect(
      statusKeyForAskResult({
        kind: "answer",
        data: { answer: "x", links: [], query_id: 1 },
      }),
    ).toBeNull();
  });
});
