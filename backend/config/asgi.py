"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-18-async-mandatory]] · [[adr-06-initial-stack]]
Docs: [[BACKEND]] · [[INFRASTRUCTURE]]
LIVE-DOC:END"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
