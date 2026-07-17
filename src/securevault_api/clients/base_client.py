"""Base HTTP client wrapping requests.Session."""

import logging
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(
        self,
        base_url,
        session=None,
        timeout=30,
        default_headers=None,
        retries=0,
        backoff_factor=0.5,
    ):
        # retries defaults to 0: this is a test framework, so we want to observe
        # server responses (including 5xx) and assert on them, not retry them away.
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = session or requests.Session()

        if default_headers:
            self.session.headers.update(default_headers)

        if retries:
            retry = Retry(
                total=retries,
                backoff_factor=backoff_factor,
                status_forcelist=(500, 502, 503, 504),
                allowed_methods=("GET", "POST", "PUT", "PATCH", "DELETE"),
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

    def set_auth_header(self, token, scheme="Bearer"):
        self.session.headers["Authorization"] = f"{scheme} {token}"

    def clear_auth_header(self):
        self.session.headers.pop("Authorization", None)

    def _build_url(self, path):
        return urljoin(self.base_url, str(path).lstrip("/"))

    def request(self, method, path, **kwargs):
        url = self._build_url(path)
        kwargs.setdefault("timeout", self.timeout)

        logger.debug("%s %s | params=%s json=%s", method, url, kwargs.get("params"), kwargs.get("json"))
        response = self.session.request(method, url, **kwargs)
        logger.debug("-> %s %s (%.3fs)", response.status_code, url, response.elapsed.total_seconds())

        return response

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
