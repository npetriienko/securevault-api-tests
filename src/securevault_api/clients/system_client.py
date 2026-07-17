"""Client for system endpoints (health check, API docs, OpenAPI spec)."""

from .base_client import BaseClient


class SystemClient(BaseClient):
    def health(self, **kwargs):
        """API health check."""
        return self.get("/health", **kwargs)

    def docs(self, **kwargs):
        """Interactive Swagger UI (OpenAPI)."""
        return self.get("/docs", **kwargs)

    def redoc(self, **kwargs):
        """ReDoc documentation."""
        return self.get("/redoc", **kwargs)

    def openapi_spec(self, **kwargs):
        """Raw OpenAPI specification."""
        return self.get("/openapi.json", **kwargs)
