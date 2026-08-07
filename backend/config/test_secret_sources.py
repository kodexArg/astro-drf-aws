"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-06-initial-stack]] · [[adr-16-m365-graph]]
Docs: [[BACKEND]] · [[VARIABLES]]
LIVE-DOC:END"""

"""adr-06 rule 6 / adr-16: `SECRET_KEY` hard-fails loudly when unset under
`DEBUG=False` (`config/test_settings.py`). This asserts the honest current
contract for the other Secrets-Manager-sourced credentials
`docs/VARIABLES.md` marks `yes` — `COGNITO_CLIENT_SECRET` and
`MSGRAPH_CLIENT_SECRET`: neither has any loud boot-time or
`check --deploy` guard, so a missing value reaches production silently and
only surfaces as a runtime failure at first use. This is a gap, not a
designed behavior — see the product finding recorded in this batch's
worker report; it is not fixed here (tests only, no product code touched)."""

import subprocess
import sys
from pathlib import Path

from django.core.management import call_command

BACKEND_DIR = Path(__file__).resolve().parent.parent

_BASE_ENV = {
    "PATH": "/usr/bin:/bin",
    "DJANGO_SETTINGS_MODULE": "config.settings",
}


def _import_settings(env_overrides, expression):
    env = dict(_BASE_ENV)
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-c", f"import config.settings as s; print({expression})"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )


def test_missing_cognito_client_secret_boots_silently_under_no_debug():
    """Honest current contract: unlike `SECRET_KEY`, a blank
    `COGNITO_CLIENT_SECRET` under `DEBUG=False` boots clean — no
    `ImproperlyConfigured`, no deploy-check error. Flip to `assert
    result.returncode != 0` only once a guard is added to product code."""
    result = _import_settings(
        {"DEBUG": "false", "SECRET_KEY": "prod-key"}, "s.COGNITO_CLIENT_SECRET"
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_missing_msgraph_client_secret_boots_silently_under_no_debug():
    result = _import_settings(
        {"DEBUG": "false", "SECRET_KEY": "prod-key"}, "s.MSGRAPH_CLIENT_SECRET"
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_check_deploy_passes_with_cognito_and_msgraph_secrets_blank(settings):
    settings.DEBUG = False
    settings.AUTH_DEV_MODE = False
    settings.SECRET_KEY = "prod-shaped-secret-key-with-enough-entropy-0123456789"
    settings.ALLOWED_HOSTS = ["example.com"]
    settings.SESSION_COOKIE_SECURE = True
    settings.CSRF_COOKIE_SECURE = True
    settings.SECURE_HSTS_SECONDS = 3600
    settings.SECURE_SSL_REDIRECT = True
    settings.COGNITO_CLIENT_SECRET = ""
    settings.MSGRAPH_CLIENT_SECRET = ""

    call_command("check", deploy=True)
