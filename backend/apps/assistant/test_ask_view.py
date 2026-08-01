"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
Governed by: [[adr-24-page-context-assistant]] · [[adr-16-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""Tests for `AskView` (POST /api/assistant/ask/) — RBAC + response contract
([[adr-24-page-context-assistant]], [[adr-10-auth]] rule 2, [[adr-16-async-mandatory]])."""

import pytest
from botocore.exceptions import BotoCoreError
from django.contrib.auth.models import Group
from django.core.management import call_command

from apps.assistant.models import AssistantQuery
from apps.router.permissions import AI_OPERATORS_GROUP
from apps.users.permissions import ADMINS_GROUP

pytestmark = pytest.mark.django_db

ASK = "/api/assistant/ask/"
MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


def _user(django_user_model, sub, groups=()):
    user = django_user_model.objects.create(sub=sub, email=f"{sub}@example.com")
    for name in groups:
        group, _ = Group.objects.get_or_create(name=name)
        user.groups.add(group)
    return user


@pytest.fixture(autouse=True)
def _cache_table():
    call_command("createcachetable")


@pytest.fixture(autouse=True)
def _mock_inference(monkeypatch):
    from apps.assistant import views
    from apps.assistant.inference import MockAssistantClient

    monkeypatch.setattr(views, "get_assistant_inference_client", MockAssistantClient)


def test_ai_operator_happy_path(client, django_user_model):
    user = _user(django_user_model, "operator-1", groups=[AI_OPERATORS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "what do I see here?", "page": "/chatui/"},
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body and body["answer"]
    assert "query_id" in body
    assert isinstance(body["links"], list)
    assert all("target" in link and "label" in link for link in body["links"])
    assert response["Cache-Control"] == "no-store"
    assert AssistantQuery.objects.filter(pk=body["query_id"], status="ok").exists()


def test_admins_member_reaches_endpoint(client, django_user_model):
    user = _user(django_user_model, "admin-1", groups=[ADMINS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/profile/"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_plain_authenticated_user_forbidden(client, django_user_model):
    user = _user(django_user_model, "plain-1")
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/chatui/"},
        content_type="application/json",
    )
    assert response.status_code == 403


def test_unauthenticated_rejected(client):
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/chatui/"},
        content_type="application/json",
    )
    assert response.status_code in (401, 403)


def test_invalid_page_rejected(client, django_user_model):
    user = _user(django_user_model, "operator-2", groups=[AI_OPERATORS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/not-in-registry/"},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_disabled_kill_switch(client, django_user_model, settings, monkeypatch):
    settings.ASSISTANT_ENABLED = False
    calls = {"n": 0}

    class _Boom:
        model_id = "should-not-run"

        def generate(self, *args, **kwargs):
            calls["n"] += 1
            raise AssertionError("inference must not run when disabled")

    from apps.assistant import views

    monkeypatch.setattr(views, "get_assistant_inference_client", _Boom)
    user = _user(django_user_model, "operator-3", groups=[AI_OPERATORS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/chatui/"},
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "disabled"
    assert "query_id" in body
    assert calls["n"] == 0
    assert AssistantQuery.objects.filter(pk=body["query_id"], status="disabled").exists()


def test_rate_blocked_returns_bare_429(client, django_user_model, monkeypatch):
    from apps.assistant import views

    monkeypatch.setattr(views, "is_rate_blocked", lambda user_id: True)
    # rebind the already-wrapped coroutine used by the view
    monkeypatch.setattr(views, "_is_rate_blocked", views.sync_to_async(lambda user_id: True))

    user = _user(django_user_model, "operator-4", groups=[AI_OPERATORS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/chatui/"},
        content_type="application/json",
    )
    assert response.status_code == 429
    assert response.content == b""
    assert "Retry-After" not in response
    assert AssistantQuery.objects.filter(user=user, status="rate_blocked").exists()


def test_throttled_burst_returns_bare_429_and_audit_row(client, django_user_model, settings):
    """The CooldownThrottle reject is a bare 429 by contract ([[API]]) —
    empty body, no Retry-After, indistinguishable from the silent rate-abuse
    block above — and still audited (`status="throttled"`)."""
    settings.THROTTLE_COOLDOWN_SECONDS = 60
    user = _user(django_user_model, "operator-7", groups=[AI_OPERATORS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)

    payload = {"utterance": "hello", "page": "/chatui/"}
    first = client.post(ASK, payload, content_type="application/json")
    second = client.post(ASK, payload, content_type="application/json")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.content == b""
    assert "Retry-After" not in second
    assert AssistantQuery.objects.filter(user=user, status="throttled").exists()


def test_bedrock_unavailable_returns_503(client, django_user_model, monkeypatch):
    from apps.assistant import views

    class _Failing:
        model_id = "fail-model"

        def generate(self, *args, **kwargs):
            raise BotoCoreError()

    monkeypatch.setattr(views, "get_assistant_inference_client", _Failing)
    user = _user(django_user_model, "operator-5", groups=[AI_OPERATORS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/chatui/"},
        content_type="application/json",
    )
    assert response.status_code == 503
    body = response.json()
    assert body["detail"] == "assistant_unavailable"
    assert "query_id" in body


def test_oor_links_from_model_are_dropped(client, django_user_model, monkeypatch):
    from apps.assistant import views

    class _WithBadLinks:
        model_id = "mock-bad-links"

        def generate(self, utterance, page_context):
            return (
                "Test answer",
                [
                    {"target": "/chatui/", "label": "Chat"},
                    {"target": "https://evil.example/", "label": "Evil"},
                ],
                1.0,
                "raw",
            )

    monkeypatch.setattr(views, "get_assistant_inference_client", _WithBadLinks)
    user = _user(django_user_model, "operator-6", groups=[AI_OPERATORS_GROUP])
    client.force_login(user, backend=MODEL_BACKEND)
    response = client.post(
        ASK,
        {"utterance": "hello", "page": "/showcase/components/"},
        content_type="application/json",
    )
    assert response.status_code == 200
    links = response.json()["links"]
    assert links == [{"target": "/chatui/", "label": "Chat"}]
