"""Assets: cross-organization data isolation (P1).

Shared fixtures (alpha_assets, beta_assets, org_beta_asset) live in
tests/api/conftest.py.
"""

import pytest

from securevault_api.data.builders import AssetBuilder
from tests.utils.assertions import assert_body_excludes, assert_status


@pytest.mark.assets
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_cross_org_asset_retrieval_is_blocked(alpha_assets, org_beta_asset):
    """TC-P1-01: an org-alpha user must not retrieve an org-beta asset by direct ID lookup."""
    # Act
    response = alpha_assets.get_asset(org_beta_asset["id"])

    # Assert: access denied, never a successful read; no org-beta data leaks
    assert_status(response, 403, 404)
    assert_body_excludes(
        response,
        org_beta_asset["name"],
        org_beta_asset["cloud_account"],
        org_beta_asset["region"],
    )


@pytest.mark.assets
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_cross_org_asset_update_is_blocked(
    alpha_assets, beta_assets, org_beta_asset, faker
):
    """TC-P1-02: an org-alpha user must not modify an org-beta asset."""
    # Arrange
    tampered = AssetBuilder(faker).build(tags={"env": "hacked"}).to_payload()

    # Act: org-alpha attempts to overwrite the org-beta asset
    response = alpha_assets.update_asset(org_beta_asset["id"], tampered)

    # Assert: update rejected, and org-beta sees the asset unchanged
    assert_status(response, 403, 404)
    after = beta_assets.get_asset(org_beta_asset["id"])
    assert_status(after, 200)
    assert after.json()["tags"] == org_beta_asset["tags"], (
        "org-beta asset was modified via cross-org update"
    )


@pytest.mark.assets
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_cross_org_asset_deletion_is_blocked(alpha_assets, beta_assets, org_beta_asset):
    """TC-P1-03: an org-alpha user (even admin) must not delete an org-beta asset."""
    # Act
    response = alpha_assets.delete_asset(org_beta_asset["id"])

    # Assert: deletion rejected, and the asset still exists for its own org
    assert_status(response, 403, 404)
    after = beta_assets.get_asset(org_beta_asset["id"])
    assert_status(after, 200)
