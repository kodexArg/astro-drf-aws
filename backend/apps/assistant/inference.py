"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
Governed by: [[adr-24-page-context-assistant]] · [[adr-16-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""Inference clients for the page-context assistant generating tier.

`BedrockAssistantClient` calls Bedrock `converse` at temperature 0 and returns
free text plus optional structured link candidates. The caller validates links
against the nav registry ([[adr-24-page-context-assistant]] rule 4). Synchronous
by design — callers wrap in `sync_to_async`, never aiobotocore
([[adr-16-async-mandatory]] rule 4).
"""

import json
import re
import time

from django.conf import settings

MOCK_MODEL_ID = "mock-assistant-inference"

_SYSTEM_PROMPT = (
    "You are a read-only page-context assistant. "
    "Never claim to perform actions, confirm operations, or change data. "
    "Use only the supplied page context. "
    "Reply with a single JSON object: "
    '{"answer":"<prose answer>","links":[{"target":"</path/>","label":"<short>"}]}. '
    "links may be empty. targets must be site-relative paths. No markdown, no HTML."
)

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _parse_model_payload(text):
    """Extract answer + raw links from model text; never raises for shape."""
    if not text:
        return "", []
    candidate = text.strip()
    match = _JSON_BLOCK.search(candidate)
    if match:
        candidate = match.group(0)
    try:
        data = json.loads(candidate)
    except (json.JSONDecodeError, TypeError):
        return text.strip(), []
    if not isinstance(data, dict):
        return text.strip(), []
    answer = data.get("answer", "")
    if not isinstance(answer, str):
        answer = str(answer) if answer is not None else ""
    links = data.get("links") or []
    if not isinstance(links, list):
        links = []
    return answer.strip(), links


class BedrockAssistantClient:
    def __init__(self, model_id=None, region=None):
        import boto3

        self.model_id = model_id or settings.ASSISTANT_BEDROCK_MODEL_ID
        self._client = boto3.client(
            "bedrock-runtime", region_name=region or settings.BEDROCK_REGION
        )

    def generate(self, utterance, page_context):
        """Return (answer_text, raw_links, latency_ms, raw_output)."""
        context_json = json.dumps(page_context, ensure_ascii=False)
        prompt = f"Page context:\n{context_json}\n\nUser question:\n{utterance}"
        started = time.monotonic()
        response = self._client.converse(
            modelId=self.model_id,
            system=[{"text": _SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.0, "maxTokens": 512},
        )
        latency_ms = (time.monotonic() - started) * 1000.0
        try:
            raw = response["output"]["message"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError, AttributeError):
            raw = ""
        answer, links = _parse_model_payload(raw)
        return answer, links, latency_ms, raw


def get_assistant_inference_client():
    if settings.DEBUG and settings.ASSISTANT_USE_MOCK_INFERENCE:
        return MockAssistantClient()
    return BedrockAssistantClient()


class MockAssistantClient:
    model_id = MOCK_MODEL_ID

    def generate(self, utterance, page_context):
        page = page_context.get("page", "/")
        answer = (
            f"Mock answer about {page}: "
            "check the current view for operational details."
        )
        links = [{"target": page, "label": "This view"}] if page else []
        raw = json.dumps({"answer": answer, "links": links}, ensure_ascii=False)
        return answer, links, 0.0, raw
