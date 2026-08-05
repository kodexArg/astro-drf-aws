"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-14-auth]]
Docs: [[BACKEND]] · [[AUTH]]
LIVE-DOC:END"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        from apps.users import checks
        from apps.users import signals
