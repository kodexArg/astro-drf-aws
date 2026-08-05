"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-25-page-context-assistant]] · [[adr-18-async-mandatory]] · [[adr-07-api-and-backend]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

"""`AskView` — page-context assistant HTTP endpoint
([[adr-25-page-context-assistant]], [[adr-18-async-mandatory]])."""

import logging

from asgiref.sync import sync_to_async
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from rest_framework.exceptions import Throttled
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistant.context import assemble_page_context
from apps.assistant.inference import get_assistant_inference_client
from apps.assistant.links import filter_registry_links
from apps.assistant.models import AssistantQuery
from apps.assistant.permissions import CanUseAssistant
from apps.assistant.serializers import AskRequestSerializer
from apps.router.rate_abuse import evaluate_rate_abuse, is_rate_blocked
from config.throttling import CooldownThrottle

_is_rate_blocked = sync_to_async(is_rate_blocked)
_evaluate_rate_abuse = sync_to_async(evaluate_rate_abuse)

logger = logging.getLogger(__name__)


def _no_store(response):
    response["Cache-Control"] = "no-store"
    return response


def _create_audit_row(
    *,
    utterance,
    page,
    answer,
    raw_model_output,
    links,
    status,
    model_id,
    latency_ms,
    user,
):
    return AssistantQuery.objects.create(
        utterance=utterance,
        page=page or "",
        answer=answer,
        raw_model_output=raw_model_output,
        links=links or [],
        status=status or "",
        model_id=model_id or "",
        latency_ms=latency_ms,
        user=user,
    )


_write_audit_row = sync_to_async(_create_audit_row)
_assemble_page_context = sync_to_async(assemble_page_context)


class AskView(APIView):
    """POST /api/assistant/ask/ — generating tier, read-only."""

    permission_classes = [IsAuthenticated, CanUseAssistant]
    throttle_classes = [CooldownThrottle]

    async def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            await sync_to_async(self.initial)(request, *args, **kwargs)

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)
            if hasattr(response, "__await__"):
                response = await response
        except Exception as exc:
            response = await sync_to_async(self.handle_exception)(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    async def post(self, request):
        request_serializer = AskRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        utterance = request_serializer.validated_data["utterance"]
        page = request_serializer.validated_data["page"]

        if await _is_rate_blocked(request.user.pk):
            await _write_audit_row(
                utterance=utterance,
                page=page,
                answer=None,
                raw_model_output=None,
                links=[],
                status="rate_blocked",
                model_id="",
                latency_ms=None,
                user=request.user,
            )
            return _no_store(Response(status=429))

        if not settings.ASSISTANT_ENABLED:
            audit_row = await _write_audit_row(
                utterance=utterance,
                page=page,
                answer=None,
                raw_model_output=None,
                links=[],
                status="disabled",
                model_id="",
                latency_ms=None,
                user=request.user,
            )
            return _no_store(
                Response({"outcome": "disabled", "query_id": audit_row.pk}, status=200)
            )

        page_context = await _assemble_page_context(request.user, page)
        client = get_assistant_inference_client()
        try:
            answer, raw_links, latency_ms, raw_output = await sync_to_async(client.generate)(
                utterance, page_context
            )
        except (BotoCoreError, ClientError):
            logger.exception("assistant inference unavailable")
            audit_row = await _write_audit_row(
                utterance=utterance,
                page=page,
                answer=None,
                raw_model_output=None,
                links=[],
                status="unavailable",
                model_id=getattr(client, "model_id", ""),
                latency_ms=None,
                user=request.user,
            )
            return _no_store(
                Response(
                    {"detail": "assistant_unavailable", "query_id": audit_row.pk},
                    status=503,
                )
            )

        links = filter_registry_links(raw_links)
        audit_row = await _write_audit_row(
            utterance=utterance,
            page=page,
            answer=answer,
            raw_model_output=raw_output,
            links=links,
            status="ok",
            model_id=getattr(client, "model_id", ""),
            latency_ms=latency_ms,
            user=request.user,
        )

        await _evaluate_rate_abuse(request.user.pk)

        return _no_store(
            Response(
                {
                    "answer": answer,
                    "links": links,
                    "query_id": audit_row.pk,
                },
                status=200,
            )
        )

    def throttled(self, request, wait):
        data = getattr(request, "data", None) or {}
        if request.user and request.user.is_authenticated:
            _create_audit_row(
                utterance=data.get("utterance") if isinstance(data, dict) else None,
                page=data.get("page", "") if isinstance(data, dict) else "",
                answer=None,
                raw_model_output=None,
                links=[],
                status="throttled",
                model_id="",
                latency_ms=None,
                user=request.user,
            )
        raise Throttled()

    def handle_exception(self, exc):
        """The CooldownThrottle reject is a bare 429 by contract ([[API]]):
        empty body, no `Retry-After`, deliberately indistinguishable from the
        silent rate-abuse block (#371) — never revealing which limiter fired.
        `no-store` comes from the cache-control middleware. DRF's
        `check_throttles` ignores `throttled()`'s return value, so the bare
        shape is rendered here instead of via `super().throttled()`."""
        if isinstance(exc, Throttled):
            return Response(status=429)
        return super().handle_exception(exc)

    def permission_denied(self, request, message=None, code=None):
        if request.user and request.user.is_authenticated:
            data = getattr(request, "data", None) or {}
            _create_audit_row(
                utterance=data.get("utterance") if isinstance(data, dict) else None,
                page=data.get("page", "") if isinstance(data, dict) else "",
                answer=None,
                raw_model_output=None,
                links=[],
                status="permission_denied",
                model_id="",
                latency_ms=None,
                user=request.user,
            )
        return super().permission_denied(request, message=message, code=code)
