import importlib
from contextlib import contextmanager

import pytest
from django.core.management import call_command
from django.urls import clear_url_caches


@pytest.fixture(scope="session", autouse=True)
def _fast_password_hasher():
    """MD5 trades PBKDF2's iteration cost for speed on a scope no test suite
    needs to prove."""
    from django.conf import settings

    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture(scope="session", autouse=True)
def _collectstatic():
    """Build the WhiteNoise manifest once per test session.

    Mirrors the `collectstatic --noinput` build step in backend/Dockerfile:
    without it, CompressedManifestStaticFilesStorage.url() raises for any
    template using {% static %} (e.g. the Django admin login page).
    """
    call_command("collectstatic", interactive=False, verbosity=0)


@pytest.fixture(autouse=True)
def _reset_authentication_backends():
    """Settings-module import bakes this from the boot env, before
    `setup_test_environment` forces `DEBUG` — recompute it live each test."""
    from django.conf import settings

    backends = ["django.contrib.auth.backends.ModelBackend"]
    if settings.DEBUG and settings.AUTH_DEV_MODE:
        backends.append("apps.users.backends.DevLoginBackend")
    settings.AUTHENTICATION_BACKENDS = backends


@contextmanager
def reload_urlconf(*modules):
    """Reload the given urlconf modules so a `DEBUG`/`AUTH_DEV_MODE` override
    takes effect, on the way in and out."""
    clear_url_caches()
    for module in modules:
        importlib.reload(module)
    try:
        yield
    finally:
        clear_url_caches()
        for module in modules:
            importlib.reload(module)
