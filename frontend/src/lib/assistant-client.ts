/* LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
 * Governed by: [[adr-04-frontend-and-design-system]]
 * Docs: [[FRONTEND]]
 * LIVE-DOC:END */

// DOM-free client for POST /api/assistant/ask/ ([[API]], [[CHATBOT]], adr-24).

export interface AssistantLink {
  target: string;
  label: string;
}

export type AssistantSuccess = {
  answer: string;
  links: AssistantLink[];
  query_id: number | string;
};

export type AssistantDisabled = {
  outcome: "disabled";
  query_id: number | string;
};

export type AskResult =
  | { kind: "answer"; data: AssistantSuccess }
  | { kind: "disabled"; data: AssistantDisabled }
  | { kind: "throttled" }
  | { kind: "unavailable" }
  | { kind: "network_error" }
  | { kind: "validation_error" };

export type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;

/**
 * POSTs `{utterance, page}` to `${backendUrl}/api/assistant/ask/`.
 * Never interprets answer as HTML — the caller renders text nodes only.
 */
export async function askAssistant(
  backendUrl: string,
  utterance: string,
  page: string,
  csrfToken: string,
  fetchImpl: FetchLike = fetch,
): Promise<AskResult> {
  try {
    const res = await fetchImpl(`${backendUrl}/api/assistant/ask/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ utterance, page }),
    });

    if (res.status === 429) return { kind: "throttled" };
    if (res.status === 400) return { kind: "validation_error" };
    if (res.status === 503) return { kind: "unavailable" };
    if (!res.ok) return { kind: "network_error" };

    const data = (await res.json()) as AssistantSuccess | AssistantDisabled;
    if ("outcome" in data && data.outcome === "disabled") {
      return { kind: "disabled", data };
    }
    if ("answer" in data && typeof data.answer === "string") {
      return {
        kind: "answer",
        data: {
          answer: data.answer,
          links: Array.isArray(data.links) ? data.links : [],
          query_id: data.query_id,
        },
      };
    }
    return { kind: "network_error" };
  } catch {
    return { kind: "network_error" };
  }
}

/** Frontend-owned status keys for non-answer assistant results (i18n MessageKeys). */
export const ASSISTANT_STATUS_COPY: Record<string, string> = {
  disabled: "assistant_outcome_disabled",
  throttled: "assistant_outcome_throttled",
  unavailable: "assistant_outcome_unavailable",
  network_error: "assistant_outcome_network_error",
  validation_error: "assistant_outcome_validation_error",
};

export function statusKeyForAskResult(result: AskResult): string | null {
  if (result.kind === "answer") return null;
  if (result.kind === "disabled") return ASSISTANT_STATUS_COPY.disabled;
  return ASSISTANT_STATUS_COPY[result.kind] ?? ASSISTANT_STATUS_COPY.network_error;
}
