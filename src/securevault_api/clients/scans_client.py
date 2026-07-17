"""Client for discovery scan endpoints (trigger, poll status)."""

from .base_client import BaseClient


class ScansClient(BaseClient):
    def trigger_scan(self, payload=None, **kwargs):
        """Trigger a new discovery scan."""
        return self.post("/scans", json=payload, **kwargs)

    def get_scan_status(self, scan_id, **kwargs):
        """Poll the status of a running or completed scan."""
        return self.get(f"/scans/{scan_id}/status", **kwargs)
