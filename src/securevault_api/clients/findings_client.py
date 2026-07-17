"""Client for finding endpoints (list, create, update status)."""

from .base_client import BaseClient


class FindingsClient(BaseClient):
    def list_findings(self, severity=None, status=None, asset_id=None, **kwargs):
        """List findings; filter by severity, status, or asset."""
        params = {}
        if severity is not None:
            params["severity"] = severity
        if status is not None:
            params["status"] = status
        if asset_id is not None:
            params["asset_id"] = asset_id
        return self.get("/findings", params=params, **kwargs)

    def create_finding(self, payload, **kwargs):
        """Create a new finding for an asset in the organization."""
        return self.post("/findings", json=payload, **kwargs)

    def update_status(self, finding_id, status, **kwargs):
        """Update finding status (open -> mitigated -> closed)."""
        payload = {"status": status}
        return self.patch(f"/findings/{finding_id}/status", json=payload, **kwargs)
