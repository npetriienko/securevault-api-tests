"""Auth: login endpoint tests."""

import pytest


@pytest.mark.auth
@pytest.mark.smoke
def test_login_with_valid_credentials_returns_tokens(settings, auth_client):
    # Arrange
    admin = settings.user("admin", "org-alpha")

    # Act
    response = auth_client.login(admin.email, admin.password)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body.get("access_token")
    assert body.get("refresh_token")
