"""Auth: unauthenticated / invalid-token access is denied (negative auth)."""

import pytest

from securevault_api.clients import AssetsClient
from tests.utils.assertions import assert_status


@pytest.fixture
def unauth_assets(settings):
    """An AssetsClient with no Authorization header."""
    return AssetsClient(settings.base_url, timeout=settings.timeout)


@pytest.mark.auth
def test_request_without_token_is_denied(unauth_assets):
    """A protected endpoint must reject a request that carries no token."""
    # Act
    response = unauth_assets.list_assets()

    # Assert
    assert_status(response, 401, 403)


@pytest.mark.auth
def test_request_with_invalid_token_is_denied(unauth_assets):
    """A malformed / garbage bearer token must be rejected."""
    # Arrange
    unauth_assets.set_auth_header("not-a-real-token")

    # Act
    response = unauth_assets.list_assets()

    # Assert
    assert_status(response, 401, 403)
