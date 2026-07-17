# Findings

Confirmed defects surfaced by the test suite against the SecureVault API.
Each entry links to the test that reproduces it.

| ID | Severity | Title | Test | Status |
|----|----------|-------|------|--------|
| F-001 | Critical | Cross-org asset access (read/update/delete) is not blocked | `tests/api/assets/test_asset_cross_org.py` (TC-P1-01/02/03), `tests/api/isolation/test_idor_and_roles.py` (TC-P1-07/08) | Open |
| F-002 | High | Deleting an asset with findings returns 500 and leaks raw SQL | _(not yet covered by a test)_ | Open |
| F-003 | High | Reports summary crashes (500, ZeroDivisionError) for an org with zero findings | `tests/api/reports/test_reports_summary.py::test_summary_empty_org` (TC-P4-01) | Open |
| F-004 | Critical | Cross-org finding status update is not blocked | `tests/api/findings/test_findings_cross_org.py::test_cross_org_finding_status_update_is_blocked` (TC-P1-05) | Open |
| F-005 | High | Severity/status filters are case-sensitive (spec requires case-insensitive) | `tests/api/search/test_findings_search.py::test_severity_filter_is_case_insensitive`, `::test_status_filter_is_case_insensitive` (TC-P3-03/04) | Open |
| F-006 | Low | `POST /scans` contract mismatch: returns 200 (spec says 201) and uses `scan_id` vs `id` | `tests/api/scans/test_scans_smoke.py` (partial) | Open |

---

## F-001 — Cross-org asset access (read/update/delete) is not blocked

**Severity:** Critical · **Status:** Open

**Endpoint:** `GET /assets/{asset_id}`, `PUT /assets/{asset_id}`, `DELETE /assets/{asset_id}`

**Summary:** A user authenticated under one organization can read, modify, and
delete assets belonging to a different organization via direct ID lookup,
breaking tenant data isolation across every asset operation.

**Reproduction:**
1. `admin@org-beta` creates an asset via `POST /assets` (stamped `org_id: org-beta`).
2. As `admin@org-alpha` (a separate organization), against `{that-id}`:
   - `GET /assets/{id}` → `200` with the full org-beta asset body.
   - `PUT /assets/{id}` with `{"tags": {"env": "hacked"}}` → `200`; the org-beta
     asset's tags are overwritten (still `org_id: org-beta`).
   - `DELETE /assets/{id}` → `200 {"message":"Asset deleted"}`; org-beta's asset
     is destroyed.

**Expected:** `403` or `404` for every operation — never `200`, no data disclosure,
no cross-org mutation or deletion.

**Observed:** All three operations succeed (`200`) against another org's asset.

**Notes:** The two accounts are genuinely separate organizations (assets carry
`org_id: org-beta`, and org-alpha authenticates with its own credentials). Tests
are intentionally left failing to track this bug.

---

## F-002 — Deleting an asset with findings returns 500 and leaks raw SQL

**Severity:** High · **Status:** Open

**Endpoint:** `DELETE /assets/{asset_id}`

**Summary:** Deleting an asset that has findings attached returns a `500`
with a raw database error in the body, instead of the documented "blocked
if open findings exist" behavior (a clean `4xx`). The response leaks the
SQL statement and schema details (information disclosure).

**Reproduction:**
1. Create an asset via `POST /assets`.
2. Create a finding on it via `POST /findings` (`asset_id` = the asset).
3. Call `DELETE /assets/{asset_id}`.

**Expected:** A clean `4xx` (e.g. `409 Conflict`) indicating the asset cannot
be deleted while findings exist — no server error, no internal details.

**Observed:** `500 Internal Server Error` with body:
```
{"error":"(sqlite3.IntegrityError) NOT NULL constraint failed: findings.asset_id
[SQL: UPDATE findings SET asset_id=? WHERE findings.id = ?] [parameters: (None, ...)]"}
```
The server attempts to null out `findings.asset_id`, violating a NOT NULL
constraint. The `500` persists even after transitioning the finding to
`closed`, so an asset with any finding attached is effectively undeletable.

**Impact:** (1) Information disclosure — raw SQL/schema leaked to clients.
(2) Test pollution — assets created in finding tests cannot be cleaned up.

**Notes:** Discovered during builder verification. Not yet covered by a
dedicated regression test.

---

## F-003 — Reports summary crashes for an org with zero findings

**Severity:** High · **Status:** Open

**Endpoint:** `GET /reports/summary`

**Summary:** For an organization with zero findings, the summary endpoint
computes a risk score as `open_findings / total_findings` and divides by
zero, returning `500` with a full Python stack trace (including source file
paths and the offending line).

**Reproduction:**
1. Authenticate as a user in an org that has no findings (e.g. a brand-new
   or empty org).
2. Call `GET /reports/summary`.

**Expected:** `200` with well-formed zeros — `total_assets`/`total_findings`/
`open_findings` = 0, severity breakdown all zero, and a defined risk score
(e.g. `0`).

**Observed:** `500 Internal Server Error` with a leaked stack trace:
```
ZeroDivisionError: division by zero
  File "/app/app/reports/router.py", line 38, in get_summary
    risk_score = round(open_findings / total_findings * 100, 1)
```

**Impact:** (1) The reports endpoint is unusable for any org until it has at
least one finding. (2) Information disclosure — internal source paths and
code leaked to clients.

**Notes:** This is the org-specific `/reports/summary` failure called out in
risk R4. `total_findings == 0` is the trigger, so only affects empty/finding-
less orgs.

---

## F-004 — Cross-org finding status update is not blocked

**Severity:** Critical · **Status:** Open

**Endpoint:** `PATCH /findings/{finding_id}/status`

**Summary:** A user in one organization can change the status of a finding
owned by a different organization, breaking tenant isolation for finding
lifecycle state.

**Reproduction:**
1. `admin@org-alpha` creates a finding (status `open`) on an org-alpha asset.
2. As `admin@org-beta`, call `PATCH /findings/{finding_id}/status` with
   `{"status": "mitigated"}`.

**Expected:** `403` or `404`; the finding's status remains `open` for org-alpha.

**Observed:** `200`, and the finding (`org_id: org-alpha`) is now `mitigated`.

**Notes:** Note that `GET /findings` listing *is* correctly org-scoped
(TC-P1-04 passes), so this is a gap specific to the status-update path, not
a blanket findings-isolation failure.

---

## F-005 — Severity/status filters are case-sensitive

**Severity:** High · **Status:** Open

**Endpoint:** `GET /findings?severity=...`, `GET /findings?status=...`

**Summary:** The findings severity and status filters only match the exact
canonical casing. The spec requires them to be case-insensitive, so callers
using a different case silently receive an empty result set instead of the
matching findings.

**Reproduction:**
1. Ensure org-alpha has at least one open finding.
2. `GET /findings?status=open` → returns the findings.
3. `GET /findings?status=OPEN` and `?status=Open` → return an empty set.
   (Same pattern for `severity`: only `CRITICAL` matches, not `critical`.)

**Expected:** All casings of a valid value return the identical set of findings.

**Observed:** Only the exact canonical case matches; other casings return `[]`.

**Impact:** Silent under-returning — a filter that looks valid quietly drops all
matches, which can hide findings from dashboards, scripts, and integrations.

---

## F-006 — `POST /scans` contract mismatch

**Severity:** Low · **Status:** Open

**Endpoint:** `POST /scans`, `GET /scans/{scan_id}/status`

**Summary:** The scan endpoints deviate from the published OpenAPI contract in
two small ways that break generated clients and schema validation.

**Observed:**
1. `POST /scans` returns **`200`** with `{"message": "Scan started",
   "scan_id": "...", "status": "IN_PROGRESS", "attempt_number": 1}`, but the
   OpenAPI spec documents a `201` response.
2. The trigger response identifies the scan as `scan_id`, while
   `GET /scans/{id}/status` returns the same value under `id` — inconsistent
   field naming across the two endpoints.

**Expected:** Response status and field names match the published `/openapi.json`
schema, and the scan identifier is named consistently.

**Notes:** Low severity (no data/security impact), but it trips OpenAPI-driven
clients and schema-conformance checks. The scans smoke test tolerates the `200`
to stay green; a strict schema-conformance test would flag it.
