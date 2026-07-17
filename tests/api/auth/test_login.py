"""Auth: login endpoint tests."""

import pytest

from tests.utils.assertions import assert_json_has, assert_status


@pytest.mark.auth
@pytest.mark.smoke
def test_login_with_valid_credentials_returns_tokens(settings, auth_client):
    # Arrange
    admin = settings.user("admin", "org-alpha")

    # Act
    response = auth_client.login(admin.email, admin.password)

    # Assert
    assert_status(response, 200)
    assert_json_has(response, "access_token", "refresh_token")
