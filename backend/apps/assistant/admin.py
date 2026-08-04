"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-25-page-context-assistant]] · [[adr-18-async-mandatory]]
Docs: [[BACKEND]] · [[CHATBOT]]
LIVE-DOC:END"""

"""Admin for AssistantQuery — raw text restricted to Assistant Auditors."""

from django.contrib import admin

from apps.assistant.models import AssistantQuery

ASSISTANT_AUDITORS_GROUP = "Assistant Auditors"
RESTRICTED_FIELDS = ("utterance", "raw_model_output", "answer")


@admin.register(AssistantQuery)
class AssistantQueryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "page", "status", "model_id", "created_at")
    readonly_fields = ("created_at",)

    def _user_is_assistant_auditor(self, request):
        user = request.user
        return user.is_superuser or user.groups.filter(name=ASSISTANT_AUDITORS_GROUP).exists()

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if self._user_is_assistant_auditor(request):
            return fields
        return [f for f in fields if f not in RESTRICTED_FIELDS]

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if self._user_is_assistant_auditor(request):
            return list_display
        return tuple(f for f in list_display if f not in RESTRICTED_FIELDS)
