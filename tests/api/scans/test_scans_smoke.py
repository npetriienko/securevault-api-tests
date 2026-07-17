"""Scans: discovery scan smoke (trigger + poll status)."""

import pytest

from tests.utils.assertions import assert_status


@pytest.mark.scans
@pytest.mark.smoke
def test_trigger_and_poll_scan(admin_alpha, scans_client_for):
    """A triggered scan is created and its status is immediately pollable."""
    # Arrange
    client = scans_client_for(admin_alpha)

    # Act: trigger a scan
    triggered = client.trigger_scan()

    # Assert: created with a scan id (API returns 200; see F-006 re: spec says 201)
    assert_status(triggered, 200, 201)
    scan_id = triggered.json()["scan_id"]

    # Act: poll its status
    status = client.get_scan_status(scan_id)

    # Assert: pollable, same scan, with a non-empty status
    assert_status(status, 200)
    body = status.json()
    assert body["id"] == scan_id
    assert body["status"], f"scan status is empty: {body}"
