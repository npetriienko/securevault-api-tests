"""Fixtures shared across API tests (auth + authenticated domain clients)."""

import pytest

from securevault_api.clients.assets_client import AssetsClient
from securevault_api.clients.auth_client import AuthClient


@pytest.fixture
def auth_client(settings):
    return AuthClient(settings.base_url)


@pytest.fixture
def require_user(settings):
    """Return a TestUser, or skip the test if its credentials are not configured."""

    def _require(role, org):
        user = settings.user(role, org)
        if not (user.email and user.password):
            pytest.skip(f"No credentials configured for {role}/{org}")
        return user

    return _require


@pytest.fixture
def login(auth_client):
    """Factory: authenticate a TestUser and return their access token."""

    def _login(user):
        response = auth_client.login(user.email, user.password)
        assert response.status_code == 200, (
            f"Login failed for {user.email}: {response.status_code} {response.text}"
        )
        return response.json()["access_token"]

    return _login


@pytest.fixture
def assets_client_for(settings, login):
    """Factory: an AssetsClient authenticated as the given TestUser."""

    def _client(user):
        client = AssetsClient(settings.base_url)
        client.set_auth_header(login(user))
        return client

    return _client
