"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-17-live-doc-backlinks]]
Governed by: [[adr-24-page-context-assistant]] · [[adr-16-async-mandatory]] · [[adr-03-api-and-backend]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

from django.urls import path

from apps.assistant import views

urlpatterns = [
    path("assistant/ask/", views.AskView.as_view(), name="assistant-ask"),
]
