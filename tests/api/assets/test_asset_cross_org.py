"""Assets: cross-organization data isolation."""

import pytest


@pytest.fixture
def org_beta_asset(require_user, assets_client_for):
    """Precondition: an asset that exists only in org-beta.

    Yields the created asset payload (incl. id); deletes it on teardown.
    """
    admin_beta = require_user("admin", "org-beta")
    client = assets_client_for(admin_beta)

    payload = {
        "name": "cross-org-isolation-probe",
        "asset_type": "S3",
        "cloud_account": "999999999999",
        "region": "eu-west-1",
        "tags": {"purpose": "isolation-test"},
    }
    response = client.create_asset(payload)
    assert response.status_code == 200, (
        f"Setup failed to create org-beta asset: {response.status_code} {response.text}"
    )
    asset = response.json()

    yield asset

    client.delete_asset(asset["id"])


@pytest.mark.assets
@pytest.mark.p1_critical
def test_cross_org_asset_retrieval_is_blocked(
    require_user, assets_client_for, org_beta_asset
):
    """TC-P1-01: an org-alpha user must not retrieve an org-beta asset by direct ID lookup."""
    # Arrange
    admin_alpha = require_user("admin", "org-alpha")
    org_alpha_client = assets_client_for(admin_alpha)

    # Act
    response = org_alpha_client.get_asset(org_beta_asset["id"])

    # Assert: access denied, never a successful read
    assert response.status_code in (403, 404), (
        f"Expected 403/404 for cross-org access, got {response.status_code}"
    )

    # Assert: no org-beta asset fields leak in the response body
    body = response.text
    for value in (
        org_beta_asset["name"],
        org_beta_asset["cloud_account"],
        org_beta_asset["region"],
    ):
        assert value not in body, f"org-beta asset data leaked: {value!r}"
