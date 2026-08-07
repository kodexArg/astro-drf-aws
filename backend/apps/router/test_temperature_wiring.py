"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-17-chatbot-two-tier]] · [[adr-18-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""adr-17 rule 7: temperature 0 is a structural constraint of the whole
choosing tier, not just `BedrockInferenceClient` in isolation
(`test_inference.py`). This proves the wiring `RouteView` actually uses —
`apps.router.views.get_inference_client`, the name the view calls — reaches
that same temperature-0 client under a non-DEBUG (production-shaped) run."""

from apps.router import views
from apps.router.inference import BedrockInferenceClient

MENU = [{"phrase": "log out"}, {"phrase": "NO_MATCH"}, {"phrase": "ESCALATE"}]


class _FakeBedrockRuntime:
    def __init__(self):
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        return {"output": {"message": {"content": [{"text": "log out"}]}}}


def test_route_view_wiring_enforces_temperature_zero(settings, monkeypatch):
    settings.DEBUG = False
    fake = _FakeBedrockRuntime()
    monkeypatch.setattr("boto3.client", lambda *a, **kw: fake)

    client = views.get_inference_client()
    assert isinstance(client, BedrockInferenceClient)

    client.choose("log me out", MENU)
    (call,) = fake.calls
    assert call["inferenceConfig"]["temperature"] == 0.0
