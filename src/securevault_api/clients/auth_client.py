"""Client for authentication endpoints (login, refresh, logout)."""

from .base_client import BaseClient


class AuthClient(BaseClient):
    def login(self, email, password, **kwargs):
        """Sign in with email + password; returns access token and refresh token."""
        payload = {"email": email, "password": password}
        return self.post("/auth/login", json=payload, **kwargs)

    def refresh(self, refresh_token, **kwargs):
        """Exchange refresh token (one-time use) for a new access token."""
        payload = {"refresh_token": refresh_token}
        return self.post("/auth/refresh", json=payload, **kwargs)

    def logout(self, refresh_token, **kwargs):
        """Revoke the refresh token and end the session."""
        payload = {"refresh_token": refresh_token}
        return self.post("/auth/logout", json=payload, **kwargs)
