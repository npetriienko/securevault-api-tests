"""Root-level pytest fixtures shared across the whole suite."""

import pytest

# Enable rich assert introspection inside the shared assertion helpers.
pytest.register_assert_rewrite("tests.utils.assertions")

from securevault_api.config.settings import load_settings


@pytest.fixture(scope="session")
def settings():
    return load_settings()
