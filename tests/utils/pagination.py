"""Helpers for working with the API's paginated list responses.

List endpoints return {"total", "page", "limit", "items": [...]}.
"""

from tests.utils.assertions import assert_status


def collect_all_items(list_call, **kwargs):
    """Page through a paginated list endpoint and return every item.

    list_call is a bound client method (e.g. findings_client.list_findings)
    accepting page/limit kwargs and returning a requests.Response.
    """
    items = []
    page = 1
    while True:
        response = list_call(page=page, **kwargs)
        assert_status(response, 200)
        body = response.json()
        batch = body["items"]
        items.extend(batch)
        if not batch or len(items) >= body["total"]:
            break
        page += 1
    return items
