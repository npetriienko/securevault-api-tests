# SecureVault API Tests

API test suite for the SecureVault service, built with **Python + pytest + requests**.

## Stack
- `pytest` — test runner
- `requests` — HTTP client
- `pytest-html` / `allure-pytest` — reporting (optional)
- `python-dotenv` — environment configuration
- `jsonschema` — response schema validation

## Layout
```
securevault-api-tests/
├── src/securevault_api/      # Reusable test framework (clients, models, config, utils)
├── tests/                    # Test cases
│   ├── api/                  # Endpoint-level tests grouped by domain
│   └── integration/          # Multi-endpoint / end-to-end flows
├── data/                     # Test payloads & JSON schemas
├── conftest.py               # Root fixtures
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Dependencies
└── .env.example              # Environment variable template
```

## Running
```bash
pip install -r requirements.txt
cp .env.example .env          # then fill in values
pytest                        # run everything
pytest -m smoke               # run a marker
pytest tests/api/auth         # run a subset
```

## Environments
Target environment is selected via the `ENV` variable (`dev` / `staging` / `prod`),
resolved in `src/securevault_api/config`.
