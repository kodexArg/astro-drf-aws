"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-14-auth]]
Docs: [[BACKEND]] · [[AUTH]]
LIVE-DOC:END"""

"""adr-14 rule 6: `manage.py check --deploy` guards production-shaped boot.
`test_auth.py` proves the failing direction only; this proves the passing
one — a production-shaped env reaches zero deploy-check errors."""

from django.core.management import call_command


def test_check_deploy_passes_under_production_shaped_env(settings):
    settings.DEBUG = False
    settings.AUTH_DEV_MODE = False
    settings.SECRET_KEY = "prod-shaped-secret-key-with-enough-entropy-0123456789"
    settings.ALLOWED_HOSTS = ["example.com"]
    settings.SESSION_COOKIE_SECURE = True
    settings.CSRF_COOKIE_SECURE = True
    settings.SECURE_HSTS_SECONDS = 3600
    settings.SECURE_SSL_REDIRECT = True

    call_command("check", deploy=True)
