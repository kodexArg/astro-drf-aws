"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-17-chatbot-two-tier]] · [[adr-18-async-mandatory]] · [[adr-07-api-and-backend]]
Docs: [[BACKEND]] · [[CHATBOT]]
API: [[API]]
LIVE-DOC:END"""

from django.urls import path

from apps.router import views

urlpatterns = [
    path("router/route/", views.RouteView.as_view(), name="router-route"),
]
