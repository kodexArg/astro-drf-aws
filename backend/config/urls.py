"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-06-initial-stack]] · [[adr-07-api-and-backend]]
Docs: [[BACKEND]]
API: [[API]]
LIVE-DOC:END"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.health.urls")),
    path("api/", include("apps.users.api_urls")),
    path("accounts/", include("apps.users.urls")),
    path("api/", include("apps.m365.urls")),
    path("api/", include("apps.router.urls")),
    path("api/", include("apps.assistant.urls")),
]
