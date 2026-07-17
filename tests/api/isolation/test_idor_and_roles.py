"""Cross-org isolation: IDOR sweep (TC-P1-07) and role coverage (TC-P1-08)."""

import pytest

from tests.utils.assertions import assert_body_excludes, assert_status
from tests.utils.pagination import collect_all_items


@pytest.mark.isolation
@pytest.mark.p1_critical
def test_idor_sweep_foreign_ids_blocked(
    admin_alpha, admin_beta, assets_client_for, findings_client_for
):
    """TC-P1-07: probing another org's asset/finding IDs must never leak data."""
    # Arrange: collect real org-alpha IDs (foreign from org-beta's perspective)
    alpha_assets = assets_client_for(admin_alpha)
    alpha_findings = findings_client_for(admin_alpha)
    foreign_asset_ids = [a["id"] for a in collect_all_items(alpha_assets.list_assets)]
    foreign_finding_asset_ids = {
        f["asset_id"] for f in collect_all_items(alpha_findings.list_findings)
    }
    assert foreign_asset_ids, "Precondition: org-alpha must have at least one asset"
    beta_assets = assets_client_for(admin_beta)
    beta_findings = findings_client_for(admin_beta)

    # Act: as org-beta, probe every foreign id and record anything that leaks
    leaks = []
    for asset_id in foreign_asset_ids:
        response = beta_assets.get_asset(asset_id)
        if response.status_code == 200:
            leaks.append(f"GET /assets/{asset_id} -> 200 (leaked)")
    for asset_id in foreign_finding_asset_ids:
        response = beta_findings.list_findings(asset_id=asset_id)
        if response.status_code == 200 and response.json()["items"]:
            count = len(response.json()["items"])
            leaks.append(f"GET /findings?asset_id={asset_id} -> {count} foreign findings")

    # Assert
    assert not leaks, "Foreign resources leaked via IDOR:\n" + "\n".join(leaks)


@pytest.mark.isolation
@pytest.mark.p1_critical
@pytest.mark.parametrize("attacker_role", ["admin", "analyst"])
def test_isolation_holds_for_all_roles(
    attacker_role, require_user, assets_client_for, org_beta_asset
):
    """TC-P1-08: cross-org isolation holds regardless of the caller's role."""
    # Arrange
    attacker = require_user(attacker_role, "org-alpha")
    client = assets_client_for(attacker)

    # Act
    response = client.get_asset(org_beta_asset["id"])

    # Assert
    assert_status(response, 403, 404)
    assert_body_excludes(
        response, org_beta_asset["name"], org_beta_asset["cloud_account"]
    )
