"""Helpers for working with the API's paginated list responses.

List endpoints return {"total", "page", "limit", "items": [...]}.
"""


def collect_all_items(list_call, **kwargs):
    """Page through a paginated list endpoint and return every item.

    list_call is a bound client method (e.g. findings_client.list_findings)
    accepting page/limit kwargs and returning a requests.Response.
    """
    items = []
    page = 1
    while True:
        response = list_call(page=page, **kwargs)
        assert response.status_code == 200, (
            f"Pagination failed on page {page}: {response.status_code} {response.text}"
        )
        body = response.json()
        batch = body["items"]
        items.extend(batch)
        if not batch or len(items) >= body["total"]:
            break
        page += 1
    return items
