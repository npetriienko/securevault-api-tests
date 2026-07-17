# SecureVault API Tests

API test suite for the SecureVault service, built with **Python + pytest + requests**.

## Stack
- `pytest` — test runner
- `requests` — HTTP client
- `pytest-html` — HTML reporting
- `python-dotenv` — environment configuration
- `jsonschema` — response schema validation

## Layout
```
securevault-api-tests/
├── src/securevault_api/      # Reusable test framework (clients, models, config, utils)
│   └── data/builders/        # Faker-based payload builders
├── tests/                    # Test cases
│   ├── api/                  # Endpoint-level tests grouped by domain
│   └── integration/          # Multi-endpoint / end-to-end flows
├── conftest.py               # Root fixtures
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Dependencies
└── .env.example              # Environment variable template
```

## Running
```bash
pip install -r requirements.txt
cp .env.example .env          # then fill in values
pytest                        # run everything (writes report.html)
pytest -m smoke               # run a marker
pytest tests/api/auth         # run a subset
```

Every run produces a self-contained `report.html` (gitignored) with results,
durations, and failure details — open it directly in a browser.

## Environments
Target environment is selected via the `ENV` variable (`dev` / `staging` / `prod`),
resolved in `src/securevault_api/config`.

## Findings
Confirmed API defects surfaced by the suite are tracked in [FINDINGS.md](FINDINGS.md).
Tests that reproduce open bugs are intentionally left failing.

## TODO
- Centralize asset create/cleanup into a shared helper/fixture so teardown is
  robust as asset tests grow (currently each test manages its own cleanup, which
  can silently fail if the client's auth state differs from creation time).
- Implement JSON Schema response validation (removed for now) so tests can assert
  responses conform to the API contract. Would live under `data/schemas/` + a
  `schema_validator` util, driven off the OpenAPI spec.
