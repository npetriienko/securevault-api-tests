# SecureVault API Tests

API test suite for the SecureVault service, built with **Python + pytest + requests**.

## Stack
- `pytest` — test runner
- `requests` — HTTP client
- `faker` — test data generation (payload builders)
- `python-dotenv` — environment / credential configuration
- `pytest-html` — self-contained HTML reporting
- `jsonschema` — OpenAPI schema conformance (reports summary)

## Layout
```
securevault-api-tests/
├── src/securevault_api/       # API-interaction toolkit
│   ├── clients/               # HTTP clients: base, auth, assets, findings,
│   │                          #   reports, scans, system
│   ├── config/                # settings.py — env + test-user loading
│   ├── models/                # asset.py, finding.py dataclasses (+ to_payload)
│   └── data/builders/         # Faker-based payload builders
├── tests/
│   ├── api/                   # endpoint tests by domain, each in its own package:
│   │                          #   assets, auth, findings, isolation, reports,
│   │                          #   scans, search
│   │   └── conftest.py        # actor + authenticated-client fixtures
│   └── utils/                 # assertions.py, pagination.py
├── conftest.py                # root fixtures (settings) + assert rewriting
├── pytest.ini                 # pytest config, markers, HTML report
├── requirements.txt           # pinned dependencies
├── .env.example               # environment variable template
└── FINDINGS.md                # confirmed API defects surfaced by the suite
```

## Running
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # then fill in base_url + per-org credentials

pytest                         # run everything (writes report.html)
pytest -m p1_critical          # run by priority marker (p1_critical..p4_medium)
pytest -m isolation            # run by domain marker (assets, findings, isolation, ...)
pytest tests/api/auth          # run a subset by path
```

Every run produces a self-contained `report.html` (gitignored) with results,
durations, and failure details — open it directly in a browser.

## Markers
- **Priority** (from the test spec): `p1_critical`, `p2_high`, `p3_high`, `p4_medium`.
- **Domain**: `auth`, `assets`, `findings`, `reports`, `scans`, `isolation`, `search`.
- **Other**: `smoke`, `regression`, `integration`.

`--strict-markers` is on, so every marker must be registered in `pytest.ini`.

## Test users & orgs
Credentials are loaded from `.env` (never committed) via `securevault_api.config`.
The suite uses three actors across two organizations:
`admin`/`analyst` in **org-alpha** (the resource-owning org) and `admin` in
**org-beta** (a separate org kept finding-free so the empty-org report case stays
reproducible). Tests skip automatically when a required credential is missing.
Target host is set by `BASE_URL`; `ENV` selects the logical environment.

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
