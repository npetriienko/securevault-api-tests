"""Environment/config loading.

Reads values from the process environment (populated via .env / python-dotenv)
and exposes a typed settings object: base_url, timeout, test users, etc.
Selects the active environment via the ENV variable.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class TestUser:
    org: str
    role: str
    email: str
    password: str


# (role, org) -> env var prefix, e.g. ADMIN_ORG_ALPHA_EMAIL / ADMIN_ORG_ALPHA_PASSWORD
TEST_USER_PREFIXES = {
    ("admin", "org-alpha"): "ADMIN_ORG_ALPHA",
    ("analyst", "org-alpha"): "ANALYST_ORG_ALPHA",
    ("admin", "org-beta"): "ADMIN_ORG_BETA",
}


def _load_user(prefix, org, role):
    email = os.environ[f"{prefix}_EMAIL"]
    password = os.environ[f"{prefix}_PASSWORD"]
    return TestUser(org=org, role=role, email=email, password=password)


@dataclass(frozen=True)
class Settings:
    env: str
    base_url: str
    timeout: int
    users: dict = field(default_factory=dict)

    def user(self, role, org):
        return self.users[(role, org)]


def load_settings():
    env = os.environ.get("ENV", "dev")
    base_url = os.environ["BASE_URL"]
    timeout = int(os.environ.get("API_TIMEOUT", 30))

    users = {
        key: _load_user(prefix, org=key[1], role=key[0])
        for key, prefix in TEST_USER_PREFIXES.items()
    }

    return Settings(env=env, base_url=base_url, timeout=timeout, users=users)
