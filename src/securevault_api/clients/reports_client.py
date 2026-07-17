"""Client for report endpoints (organization security posture summary)."""

from .base_client import BaseClient


class ReportsClient(BaseClient):
    def get_summary(self, **kwargs):
        """Return the organization-wide security posture summary."""
        return self.get("/reports/summary", **kwargs)
