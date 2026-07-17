"""Environment/config loading.

Reads values from the process environment (populated via .env / python-dotenv)
and exposes a typed settings object: base_url, timeout, credentials, etc.
Selects the active environment via the ENV variable.
"""

# class Settings:
#     base_url: str
#     timeout: int
#     ...
#
# def load_settings() -> "Settings":
#     ...
