"""Fixtures shared across API tests (auth + authenticated domain clients)."""

import pytest

from securevault_api.clients.assets_client import AssetsClient
from securevault_api.clients.auth_client import AuthClient
from securevault_api.clients.findings_client import FindingsClient
from securevault_api.clients.reports_client import ReportsClient
from securevault_api.data.builders import AssetBuilder, FindingBuilder
from tests.utils.assertions import assert_status


@pytest.fixture
def auth_client(settings):
    return AuthClient(settings.base_url)


@pytest.fixture
def require_user(settings):
    """Return a TestUser, or skip the test if its credentials are not configured."""

    def _require(role, org):
        user = settings.user(role, org)
        if not (user.email and user.password):
            pytest.skip(f"No credentials configured for {role}/{org}")
        return user

    return _require


@pytest.fixture(scope="session")
def _token_cache():
    """Per-session cache of access tokens, keyed by email.

    Login is rate-limited, so tokens are fetched once per user per session and
    reused across all tests/clients.
    """
    return {}


@pytest.fixture
def login(settings, _token_cache):
    """Factory: authenticate a TestUser and return their (cached) access token."""

    def _login(user):
        if user.email not in _token_cache:
            client = AuthClient(settings.base_url)
            response = client.login(user.email, user.password)
            assert response.status_code == 200, (
                f"Login failed for {user.email}: {response.status_code} {response.text}"
            )
            _token_cache[user.email] = response.json()["access_token"]
        return _token_cache[user.email]

    return _login


@pytest.fixture
def client_for(settings, login):
    """Factory: a domain client of the given class, authenticated as a TestUser."""

    def _client(client_cls, user):
        client = client_cls(settings.base_url)
        client.set_auth_header(login(user))
        return client

    return _client


@pytest.fixture
def assets_client_for(client_for):
    """Factory: an AssetsClient authenticated as the given TestUser."""
    return lambda user: client_for(AssetsClient, user)


@pytest.fixture
def findings_client_for(client_for):
    """Factory: a FindingsClient authenticated as the given TestUser."""
    return lambda user: client_for(FindingsClient, user)


@pytest.fixture
def reports_client_for(client_for):
    """Factory: a ReportsClient authenticated as the given TestUser."""
    return lambda user: client_for(ReportsClient, user)


# --- Actors -----------------------------------------------------------------
# org-alpha is the resource-owning org (pre-seeded with assets/findings).
# org-beta is a separate org kept empty, used as the "other org" / attacker.


@pytest.fixture
def admin_alpha(require_user):
    return require_user("admin", "org-alpha")


@pytest.fixture
def analyst_alpha(require_user):
    return require_user("analyst", "org-alpha")


@pytest.fixture
def admin_beta(require_user):
    return require_user("admin", "org-beta")


# --- Shared domain clients / seed data --------------------------------------


@pytest.fixture
def alpha_assets(admin_alpha, assets_client_for):
    return assets_client_for(admin_alpha)


@pytest.fixture
def beta_assets(admin_beta, assets_client_for):
    return assets_client_for(admin_beta)


@pytest.fixture
def org_beta_asset(beta_assets, faker):
    """An asset that exists only in org-beta. Yields it; deletes on teardown."""
    response = beta_assets.create_asset(AssetBuilder(faker).build().to_payload())
    assert_status(response, 200)
    asset = response.json()

    yield asset

    beta_assets.delete_asset(asset["id"])


@pytest.fixture
def alpha_asset(alpha_assets, faker):
    """A fresh asset owned by org-alpha (the resource-owning org). Returns the dict.

    org-beta is deliberately kept finding-free so TC-P4-01 stays reproducible, so
    findings are created in org-alpha instead.
    """
    response = alpha_assets.create_asset(AssetBuilder(faker).build().to_payload())
    assert_status(response, 200)
    asset = response.json()

    yield asset

    # F-002: an asset with findings can't be deleted; best-effort cleanup only.
    alpha_assets.delete_asset(asset["id"])


@pytest.fixture
def make_alpha_finding(admin_alpha, findings_client_for, faker):
    """Factory: create a finding on an org-alpha asset and return the created dict."""
    client = findings_client_for(admin_alpha)

    def _make(asset_id, **overrides):
        payload = FindingBuilder(faker).build(asset_id=asset_id, **overrides).to_payload()
        response = client.create_finding(payload)
        assert_status(response, 200, 201)
        return response.json()

    return _make


@pytest.fixture
def org_alpha_finding(alpha_asset, make_alpha_finding):
    """A single org-alpha finding (severity HIGH, status open) on a fresh asset."""
    return make_alpha_finding(alpha_asset["id"], severity="HIGH")


@pytest.fixture
def refetch_finding(admin_alpha, findings_client_for):
    """Return the current server state of an org-alpha finding by id (via list)."""
    client = findings_client_for(admin_alpha)

    def _refetch(asset_id, finding_id):
        items = client.list_findings(asset_id=asset_id).json()["items"]
        return next((f for f in items if f["id"] == finding_id), None)

    return _refetch
