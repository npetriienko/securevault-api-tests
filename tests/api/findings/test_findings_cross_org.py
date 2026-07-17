"""Findings: cross-organization data isolation (P1)."""

import pytest

from tests.utils.assertions import assert_status


@pytest.mark.findings
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_cross_org_findings_list_isolation(
    admin_beta, findings_client_for, org_alpha_finding
):
    """TC-P1-04: org-beta must not see org-alpha findings by asset filter or in its list."""
    # Arrange
    beta_findings = findings_client_for(admin_beta)
    alpha_finding_id = org_alpha_finding["id"]
    alpha_asset_id = org_alpha_finding["asset_id"]

    # Act: filter by org-alpha's asset id, and read org-beta's own findings list
    # (bounded first page -- org-beta's list must not surface a foreign finding).
    filtered = beta_findings.list_findings(asset_id=alpha_asset_id)
    listed = beta_findings.list_findings(page=1, limit=100)

    # Assert: neither path exposes the org-alpha finding
    assert_status(filtered, 200, 403, 404)
    if filtered.status_code == 200:
        filtered_ids = [f["id"] for f in filtered.json()["items"]]
        assert alpha_finding_id not in filtered_ids, "org-alpha finding leaked via asset filter"
    assert_status(listed, 200)
    listed_ids = [f["id"] for f in listed.json()["items"]]
    assert alpha_finding_id not in listed_ids, "org-alpha finding leaked in org-beta list"


@pytest.mark.findings
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_cross_org_finding_status_update_is_blocked(
    admin_beta, findings_client_for, org_alpha_finding, refetch_finding
):
    """TC-P1-05: org-beta must not change the status of an org-alpha finding."""
    # Arrange
    beta_findings = findings_client_for(admin_beta)
    finding_id = org_alpha_finding["id"]
    asset_id = org_alpha_finding["asset_id"]

    # Act: org-beta tries to mitigate org-alpha's finding
    response = beta_findings.update_status(finding_id, {"status": "mitigated"})

    # Assert: rejected, and org-alpha still sees the finding as "open"
    assert_status(response, 403, 404)
    current = refetch_finding(asset_id, finding_id)
    assert current is not None, "org-alpha finding disappeared after cross-org update"
    assert current["status"] == "open", "org-alpha finding status changed cross-org"
