"""Reusable custom assertion helpers for working with API responses."""


def assert_status(response, *expected):
    """Assert the response status code is one of the expected values."""
    assert response.status_code in expected, (
        f"Expected status in {expected}, got {response.status_code}: {response.text}"
    )


def assert_body_excludes(response, *values):
    """Assert none of the given values appear anywhere in the response body.

    Useful for leak detection: a sensitive value must not surface in any field
    or error message, not just the ones we think to check.
    """
    body = response.text
    for value in values:
        assert value not in body, f"Leaked value in response: {value!r}"
