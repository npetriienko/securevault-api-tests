"""Client for asset endpoints (list, create, retrieve, update, delete)."""

from .base_client import BaseClient


class AssetsClient(BaseClient):
    def list_assets(self, asset_type=None, page=None, limit=None, **kwargs):
        """List all assets for the organization (paginated; filter by asset_type)."""
        params = {}
        if asset_type is not None:
            params["asset_type"] = asset_type
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        return self.get("/assets", params=params, **kwargs)

    def create_asset(self, payload, **kwargs):
        """Create a new asset."""
        return self.post("/assets", json=payload, **kwargs)

    def get_asset(self, asset_id, **kwargs):
        """Retrieve a single asset by ID."""
        return self.get(f"/assets/{asset_id}", **kwargs)

    def update_asset(self, asset_id, payload, **kwargs):
        """Update an existing asset."""
        return self.put(f"/assets/{asset_id}", json=payload, **kwargs)

    def delete_asset(self, asset_id, **kwargs):
        """Delete an asset (admin only; blocked if open findings exist)."""
        return self.delete(f"/assets/{asset_id}", **kwargs)
