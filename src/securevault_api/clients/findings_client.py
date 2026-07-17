"""Client for finding endpoints (list, create, update status)."""

from .base_client import BaseClient


class FindingsClient(BaseClient):
    def list_findings(
        self, severity=None, status=None, asset_id=None, page=None, limit=None, **kwargs
    ):
        """List findings; filter by severity, status, or asset (paginated)."""
        params = {}
        if severity is not None:
            params["severity"] = severity
        if status is not None:
            params["status"] = status
        if asset_id is not None:
            params["asset_id"] = asset_id
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        return self.get("/findings", params=params, **kwargs)

    def create_finding(self, payload, **kwargs):
        """Create a new finding for an asset in the organization."""
        return self.post("/findings", json=payload, **kwargs)

    def update_status(self, finding_id, payload, **kwargs):
        """Update finding status (open -> mitigated -> closed).

        payload is the full request body, so tests can also probe extra/unexpected
        fields (e.g. a mass-assignment attempt) rather than only {"status": ...}.
        """
        return self.patch(f"/findings/{finding_id}/status", json=payload, **kwargs)
