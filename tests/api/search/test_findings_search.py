"""Search / retrieval correctness: filters and pagination (P3)."""

import math

import pytest

from tests.utils.assertions import assert_status
from tests.utils.pagination import collect_all_items


@pytest.mark.search
@pytest.mark.p3_high
@pytest.mark.parametrize("endpoint", ["assets", "findings"])
def test_pagination_page_zero_is_well_defined(
    endpoint, alpha_assets, admin_alpha, findings_client_for
):
    """TC-P3-01: page=0 is a validation error or a consistent, non-crashing response."""
    # Arrange
    if endpoint == "assets":
        list_call = alpha_assets.list_assets
    else:
        list_call = findings_client_for(admin_alpha).list_findings

    # Act
    first = list_call(page=0)
    second = list_call(page=0)

    # Assert: documented as 1-based, so page=0 must be well-defined and never a 500
    assert first.status_code != 500, f"page=0 crashed: {first.text}"
    assert_status(first, 200, 400, 422)
    assert first.status_code == second.status_code
    if first.status_code == 200:
        assert first.json()["items"] == second.json()["items"], (
            "page=0 returns non-deterministic results"
        )


@pytest.mark.search
@pytest.mark.p3_high
def test_pagination_beyond_last_page_is_empty(alpha_assets):
    """TC-P3-02: a page past the last returns an empty set, not an error or wraparound."""
    # Arrange
    first = alpha_assets.list_assets(page=1)
    assert_status(first, 200)
    body = first.json()
    last_page = max(1, math.ceil(body["total"] / body["limit"]))

    # Act
    beyond = alpha_assets.list_assets(page=last_page + 1)

    # Assert
    assert_status(beyond, 200)
    assert beyond.json()["items"] == [], "beyond-last-page should return empty items"
    if body["items"]:
        assert beyond.json()["items"] != body["items"], "page wrapped around to page 1"


@pytest.mark.search
@pytest.mark.p3_high
def test_severity_filter_is_case_insensitive(
    admin_alpha, findings_client_for, alpha_asset, make_alpha_finding
):
    """TC-P3-03: severity filter returns the same set regardless of case."""
    # Arrange
    make_alpha_finding(alpha_asset["id"], severity="CRITICAL")
    client = findings_client_for(admin_alpha)

    # Act
    result_sets = [
        {f["id"] for f in collect_all_items(client.list_findings, severity=value)}
        for value in ("critical", "CRITICAL", "Critical")
    ]

    # Assert
    assert result_sets[0], "expected at least one CRITICAL finding"
    assert result_sets[0] == result_sets[1] == result_sets[2], (
        f"severity filter is case-sensitive: {result_sets}"
    )


@pytest.mark.search
@pytest.mark.p3_high
def test_status_filter_is_case_insensitive(
    admin_alpha, findings_client_for, org_alpha_finding
):
    """TC-P3-04: status filter returns the same set regardless of case."""
    # Arrange (org_alpha_finding guarantees at least one "open" finding exists)
    client = findings_client_for(admin_alpha)

    # Act
    result_sets = [
        {f["id"] for f in collect_all_items(client.list_findings, status=value)}
        for value in ("open", "OPEN", "Open")
    ]

    # Assert
    assert result_sets[0], "expected at least one open finding"
    assert result_sets[0] == result_sets[1] == result_sets[2], (
        f"status filter is case-sensitive: {result_sets}"
    )


@pytest.mark.search
@pytest.mark.p3_high
def test_findings_count_matches_created(
    admin_alpha, findings_client_for, alpha_asset, make_alpha_finding
):
    """TC-P3-05: every created finding is retrievable exactly once across pages.

    Scaled down (5 findings, limit=2 to force paging) rather than the spec's 25,
    since findings cannot be deleted (F-002) and would permanently accumulate.
    """
    # Arrange
    created = {make_alpha_finding(alpha_asset["id"], severity="LOW")["id"] for _ in range(5)}
    client = findings_client_for(admin_alpha)

    # Act
    retrieved = [
        f["id"]
        for f in collect_all_items(client.list_findings, asset_id=alpha_asset["id"], limit=2)
    ]

    # Assert
    assert len(retrieved) == len(set(retrieved)), "duplicate findings across pages"
    assert set(retrieved) == created, (
        f"count mismatch: created {len(created)}, retrieved {len(set(retrieved))}"
    )


@pytest.mark.search
@pytest.mark.p3_high
@pytest.mark.parametrize(
    "severity,status",
    [("CRITICAL", "open"), ("HIGH", "mitigated"), ("LOW", "closed")],
)
def test_filter_combination_returns_seeded_match(
    severity, status, admin_alpha, findings_client_for, alpha_asset, make_alpha_finding
):
    """TC-P3-06: a (severity, status) filter never drops a finding that matches it.

    Samples representative combinations rather than the full 5x3 matrix to limit
    undeletable test data (F-002).
    """
    # Arrange: create a finding and drive it to the target status
    finding = make_alpha_finding(alpha_asset["id"], severity=severity)
    client = findings_client_for(admin_alpha)
    if status != "open":
        assert_status(client.update_status(finding["id"], {"status": status}), 200)

    # Act
    items = collect_all_items(
        client.list_findings, asset_id=alpha_asset["id"], severity=severity, status=status
    )

    # Assert
    ids = {f["id"] for f in items}
    assert finding["id"] in ids, (
        f"({severity}, {status}) filter dropped a matching finding"
    )


@pytest.mark.search
@pytest.mark.p3_high
def test_new_finding_is_immediately_searchable(
    admin_alpha, findings_client_for, alpha_asset, make_alpha_finding
):
    """TC-P3-07: a newly created finding appears in the very next list call."""
    # Arrange
    finding = make_alpha_finding(alpha_asset["id"], severity="MEDIUM")
    client = findings_client_for(admin_alpha)

    # Act
    items = client.list_findings(asset_id=alpha_asset["id"]).json()["items"]

    # Assert
    ids = {f["id"] for f in items}
    assert finding["id"] in ids, "newly created finding was not immediately searchable"
