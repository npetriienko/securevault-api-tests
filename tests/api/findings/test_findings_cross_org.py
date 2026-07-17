"""Findings: cross-organization data isolation (P1)."""

import pytest

from tests.utils.assertions import assert_status
from tests.utils.pagination import collect_all_items


@pytest.mark.findings
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_cross_org_findings_list_isolation(
    admin_beta, findings_client_for, org_alpha_finding
):
    """TC-P1-04: org-beta must not see org-alpha findings by asset filter or in its list."""
    beta_findings = findings_client_for(admin_beta)
    alpha_finding_id = org_alpha_finding["id"]
    alpha_asset_id = org_alpha_finding["asset_id"]

    # Filtering on org-alpha's asset id returns nothing (or is denied) — never data
    filtered = beta_findings.list_findings(asset_id=alpha_asset_id)
    assert_status(filtered, 200, 403, 404)
    if filtered.status_code == 200:
        ids = [f["id"] for f in filtered.json()["items"]]
        assert alpha_finding_id not in ids, "org-alpha finding leaked via asset filter"

    # org-beta's own (unfiltered) list must never contain org-alpha's finding
    all_ids = [f["id"] for f in collect_all_items(beta_findings.list_findings)]
    assert alpha_finding_id not in all_ids, "org-alpha finding leaked in org-beta list"


@pytest.mark.findings
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_cross_org_finding_status_update_is_blocked(
    admin_alpha, admin_beta, findings_client_for, org_alpha_finding
):
    """TC-P1-05: org-beta must not change the status of an org-alpha finding."""
    beta_findings = findings_client_for(admin_beta)
    alpha_findings = findings_client_for(admin_alpha)
    finding_id = org_alpha_finding["id"]
    asset_id = org_alpha_finding["asset_id"]

    # Attack: org-beta tries to mitigate org-alpha's finding
    response = beta_findings.update_status(finding_id, {"status": "mitigated"})
    assert_status(response, 403, 404)

    # Verify via org-alpha: status is still "open"
    items = alpha_findings.list_findings(asset_id=asset_id).json()["items"]
    current = next(f for f in items if f["id"] == finding_id)
    assert current["status"] == "open", "org-alpha finding status changed cross-org"
