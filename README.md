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
├── src/securevault_api/      # API-interaction toolkit (clients, models, config, builders)
│   └── data/builders/        # Faker-based payload builders
├── tests/                    # Test cases
│   ├── api/                  # Endpoint-level tests grouped by domain
│   └── utils/                # Test-support helpers (custom assertions)
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

## TODO (remaining review findings)

Resilience & correctness
- Token refresh-on-401: the session token cache never refreshes, so a token that
  expires mid-run leaves every later call failing. Add a 401 -> `AuthClient.refresh`
  -> retry-once wrapper, and guard the cache's check-then-set with a lock.
- Centralize asset create/cleanup into a shared helper/fixture so teardown is
  robust as asset tests grow (each test currently manages its own cleanup).

Contract & coverage
- Reusable OpenAPI schema-conformance assertion: generalize TC-P4-04 into
  `assert_matches_schema(response, "<path>")` driven off `/openapi.json`, and
  migrate off the deprecated `jsonschema.RefResolver` (use `referencing`). This
  also revives the removed JSON Schema response-validation idea.
- Broaden coverage: scan negative/failure paths, `AuthClient.refresh`/`logout`
  lifecycle, and more auth edge cases (expired token, wrong-org token).

Tooling & ergonomics
- Add `pyproject.toml` so `securevault_api` is an installable package (`pip install
  -e .`) and tool/pytest config lives in one place.
- Add a linter/formatter (e.g. `ruff`) to codify style and catch dead imports.
- Attach the failing request/response to the pytest-html report for faster triage.
- Consider a fluent assertion library (`assertpy`, `dirty-equals`) as the suite grows.
- Enable parallel execution (`pytest-xdist`, `-n auto`) to speed up runs. Needs
  test isolation work first: avoid shared-state collisions (e.g. org-beta empty-org
  assumption in TC-P4-01) and confirm the token cache/rate limiting hold up under
  concurrent workers.

Design decisions to settle
- Finalize the assertions boundary: shared helpers in `tests/utils/assertions.py`
  vs inline test-specific asserts, applied consistently (some domain checks remain
  inline by design).
- Decide the role of `Asset`/`Finding` models: lean in (parse responses into typed
  models with `from_response`) or keep them as payload-builders only.
- Response-time/SLA assertion helper + perf marker (currently inlined once in TC-P4-03).
