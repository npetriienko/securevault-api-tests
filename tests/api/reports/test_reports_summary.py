"""Reports: org-scoped summary (P1) and endpoint reliability (P4)."""

import jsonschema
import pytest

from securevault_api.clients import SystemClient
from securevault_api.data.builders import AssetBuilder
from tests.utils.assertions import assert_status


@pytest.mark.reports
@pytest.mark.isolation
@pytest.mark.p1_critical
def test_reports_summary_is_org_scoped(
    admin_alpha, admin_beta, reports_client_for, assets_client_for, faker
):
    """TC-P1-06: a summary's asset count is org-scoped.

    Creating an asset in another org (org-beta) must not change the caller's
    total_assets. Findings/risk-score scoping isn't exercised here: seeding an
    org-beta finding would pollute org-beta (breaking the empty-org case
    TC-P4-01) and can't be undone (findings aren't deletable -- F-002).
    """
    # Arrange: baseline org-alpha summary, then add an asset in a different org
    alpha_reports = reports_client_for(admin_alpha)
    before = alpha_reports.get_summary()
    assert_status(before, 200)
    body = before.json()
    assert body["org_id"] == "org-alpha"
    assets_before = body["total_assets"]

    beta_assets = assets_client_for(admin_beta)
    beta_asset = beta_assets.create_asset(AssetBuilder(faker).build().to_payload()).json()
    try:
        # Act
        after = alpha_reports.get_summary()

        # Assert: org-alpha's count is unaffected by the org-beta asset
        assert_status(after, 200)
        assert after.json()["total_assets"] == assets_before, (
            "org-alpha summary count changed after an org-beta asset was created"
        )
    finally:
        beta_assets.delete_asset(beta_asset["id"])


@pytest.mark.reports
@pytest.mark.p4_medium
def test_summary_empty_org(admin_beta, reports_client_for):
    """TC-P4-01: summary for an org with zero findings returns well-formed zeros."""
    # Act
    response = reports_client_for(admin_beta).get_summary()

    # Assert
    assert_status(response, 200)
    body = response.json()
    assert body["total_findings"] == 0, f"expected zero findings: {body}"
    assert body["open_findings"] == 0, f"expected zero open findings: {body}"
    assert all(count == 0 for count in body["severity_breakdown"].values()), (
        f"expected all-zero severity breakdown: {body['severity_breakdown']}"
    )
    assert body["risk_score_percent"] is not None, "risk_score_percent should be defined"


@pytest.mark.reports
@pytest.mark.p4_medium
def test_summary_closed_findings_only(reports_client_for):
    """TC-P4-02: summary aggregates correctly when all findings are closed."""
    pytest.skip(
        "Requires a dedicated org whose findings are all closed. Only org-alpha "
        "(has open findings) and org-beta (kept finding-free for TC-P4-01) are "
        "available, and findings cannot be deleted (F-002) to reset an org."
    )


@pytest.mark.reports
@pytest.mark.p4_medium
def test_summary_performance(admin_alpha, reports_client_for):
    """TC-P4-03 (scaled down): summary responds within the time budget.

    The spec calls for 500 assets / 2000 findings, but bulk-seeding the shared
    server is infeasible and unrecoverable (F-002), so this runs against
    org-alpha's existing dataset as a performance smoke.
    """
    # Act
    response = reports_client_for(admin_alpha).get_summary()

    # Assert
    assert_status(response, 200)
    assert response.elapsed.total_seconds() < 2.0, (
        f"summary too slow: {response.elapsed.total_seconds():.2f}s"
    )


@pytest.mark.reports
@pytest.mark.p4_medium
def test_summary_matches_openapi_schema(admin_alpha, reports_client_for, settings):
    """TC-P4-04: summary response conforms to the schema published at /openapi.json."""
    # Arrange: pull the summary response schema from the OpenAPI spec
    spec = SystemClient(settings.base_url).openapi_spec().json()
    schema = (
        spec["paths"]["/reports/summary"]["get"]["responses"]["200"]
        ["content"]["application/json"]["schema"]
    )
    resolver = jsonschema.RefResolver.from_schema(spec)

    # Act
    response = reports_client_for(admin_alpha).get_summary()

    # Assert
    assert_status(response, 200)
    jsonschema.validate(instance=response.json(), schema=schema, resolver=resolver)
