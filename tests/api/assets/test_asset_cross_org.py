"""Assets: cross-organization data isolation."""

import pytest

from securevault_api.data.builders import AssetBuilder
from tests.utils.assertions import assert_body_excludes, assert_status


@pytest.fixture
def org_beta_asset(require_user, assets_client_for, faker):
    """Precondition: an asset that exists only in org-beta.
    Yields the created asset payload (incl. id); deletes it on teardown.
    """
    admin_beta = require_user("admin", "org-beta")
    client = assets_client_for(admin_beta)

    payload = AssetBuilder(faker).build().to_payload()
    response = client.create_asset(payload)
    assert_status(response, 200)
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
    assert_status(response, 403, 404)

    # Assert: no org-beta asset fields leak in the response body
    assert_body_excludes(
        response,
        org_beta_asset["name"],
        org_beta_asset["cloud_account"],
        org_beta_asset["region"],
    )
