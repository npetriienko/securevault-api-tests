"""Root-level pytest fixtures shared across the whole suite."""

import pytest

from securevault_api.config.settings import load_settings


@pytest.fixture(scope="session")
def settings():
    return load_settings()
