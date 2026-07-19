"""Assets: deletion integrity when findings are attached (F-002 regression)."""

import pytest

from tests.utils.assertions import assert_body_excludes, assert_status


@pytest.mark.assets
@pytest.mark.p2_high
def test_delete_asset_with_findings_is_blocked_cleanly(
    alpha_assets, alpha_asset, make_alpha_finding
):
    """F-002: deleting an asset that has findings must be a clean 4xx, not a 500 SQL leak.

    The spec says deletion is "blocked if open findings exist", so it should return
    a clean client error (e.g. 409 Conflict) -- never a 500, and never leaking the
    underlying SQL/schema in the response body.
    """
    # Arrange: an org-alpha asset with a finding attached
    make_alpha_finding(alpha_asset["id"], severity="LOW")

    # Act
    response = alpha_assets.delete_asset(alpha_asset["id"])

    # Assert: blocked with a clean client error (never a 5xx crash)...
    assert_status(response, 400, 403, 409, 422)
    # ...and the response must not leak database internals.
    assert_body_excludes(response, "sqlite", "IntegrityError", "NOT NULL", "Traceback")
