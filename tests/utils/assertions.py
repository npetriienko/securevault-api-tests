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


def assert_no_server_error(response):
    """Assert the response is not a 5xx server error (e.g. an unhandled crash)."""
    assert response.status_code < 500, (
        f"Unexpected server error: {response.status_code} {response.text}"
    )


def assert_json_has(response, *keys):
    """Assert the JSON body is an object with each key present and truthy (non-empty)."""
    body = response.json()
    for key in keys:
        assert body.get(key), f"Response missing/empty field {key!r}: {body}"
