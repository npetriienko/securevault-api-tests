"""Findings: severity immutability and update-scope integrity (P2)."""

import concurrent.futures

import pytest

from tests.utils.assertions import assert_status


@pytest.mark.findings
@pytest.mark.p2_high
def test_severity_immutable_across_lifecycle(
    admin_alpha, findings_client_for, org_alpha_finding, refetch_finding
):
    """TC-P2-01: severity is unchanged as status moves open -> mitigated -> closed."""
    client = findings_client_for(admin_alpha)
    finding_id = org_alpha_finding["id"]
    asset_id = org_alpha_finding["asset_id"]
    assert org_alpha_finding["severity"] == "HIGH"

    assert_status(client.update_status(finding_id, {"status": "mitigated"}), 200)
    assert refetch_finding(asset_id, finding_id)["severity"] == "HIGH"

    assert_status(client.update_status(finding_id, {"status": "closed"}), 200)
    assert refetch_finding(asset_id, finding_id)["severity"] == "HIGH"


@pytest.mark.findings
@pytest.mark.p2_high
def test_severity_not_overwritten_via_mass_assignment(
    admin_alpha, findings_client_for, alpha_asset, make_alpha_finding, refetch_finding
):
    """TC-P2-02: a stray 'severity' field in a status update is ignored, not applied."""
    finding = make_alpha_finding(alpha_asset["id"], severity="MEDIUM")
    client = findings_client_for(admin_alpha)

    response = client.update_status(
        finding["id"], {"status": "mitigated", "severity": "CRITICAL"}
    )
    # Either the extra field is rejected (400) or accepted-but-ignored (200).
    assert_status(response, 200, 400)

    after = refetch_finding(alpha_asset["id"], finding["id"])
    assert after["severity"] == "MEDIUM", "severity was overwritten via mass-assignment"


@pytest.mark.findings
@pytest.mark.p2_high
def test_concurrent_status_updates_do_not_corrupt(
    admin_alpha, findings_client_for, alpha_asset, make_alpha_finding, refetch_finding
):
    """TC-P2-03: concurrent status PATCHes leave a valid state and intact severity."""
    finding = make_alpha_finding(alpha_asset["id"], severity="LOW")
    finding_id = finding["id"]

    def patch(status):
        # Each thread gets its own client/session (cached token reused).
        return findings_client_for(admin_alpha).update_status(
            finding_id, {"status": status}
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(patch, ["mitigated", "closed"]))

    for response in results:
        assert response.status_code != 500, f"500 under concurrency: {response.text}"

    after = refetch_finding(alpha_asset["id"], finding_id)
    assert after["status"] in ("mitigated", "closed"), (
        f"corrupted status: {after['status']!r}"
    )
    assert after["severity"] == "LOW"


@pytest.mark.findings
@pytest.mark.p2_high
def test_status_update_changes_only_status(
    admin_alpha, findings_client_for, alpha_asset, make_alpha_finding, refetch_finding
):
    """TC-P2-04: a status update mutates only the status field, nothing else."""
    finding = make_alpha_finding(
        alpha_asset["id"], severity="MEDIUM", cve_id="CVE-2024-0001"
    )
    finding_id = finding["id"]

    before = refetch_finding(alpha_asset["id"], finding_id)
    assert_status(
        findings_client_for(admin_alpha).update_status(finding_id, {"status": "mitigated"}),
        200,
    )
    after = refetch_finding(alpha_asset["id"], finding_id)

    # status is expected to change; updated_at is an expected side effect.
    ignore = {"status", "updated_at"}
    diffs = {
        key: (before[key], after[key])
        for key in before
        if key not in ignore and before[key] != after[key]
    }
    assert not diffs, f"status update changed unrelated fields: {diffs}"
    assert before["status"] == "open" and after["status"] == "mitigated"
