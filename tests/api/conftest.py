"""Fixtures shared across API tests (e.g. domain clients built on api_client)."""

import pytest

from securevault_api.clients.auth_client import AuthClient


@pytest.fixture
def auth_client(settings):
    return AuthClient(settings.base_url)
