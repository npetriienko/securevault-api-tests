# Findings

Confirmed defects surfaced by the test suite against the SecureVault API.
Each entry links to the test that reproduces it.

| ID | Severity | Title | Test | Status |
|----|----------|-------|------|--------|
| F-001 | Critical | Cross-org asset retrieval is not blocked | `tests/api/assets/test_asset_cross_org.py::test_cross_org_asset_retrieval_is_blocked` (TC-P1-01) | Open |
| F-002 | High | Deleting an asset with findings returns 500 and leaks raw SQL | _(not yet covered by a test)_ | Open |

---

## F-001 — Cross-org asset retrieval is not blocked

**Severity:** Critical · **Status:** Open

**Endpoint:** `GET /assets/{asset_id}`

**Summary:** A user authenticated under one organization can retrieve an
asset that belongs to a different organization via direct ID lookup,
breaking tenant data isolation.

**Reproduction:**
1. `admin@org-beta` creates an asset via `POST /assets` (asset is stamped `org_id: org-beta`).
2. `admin@org-alpha` (a separate organization) calls `GET /assets/{that-id}`.
3. The API returns `200 OK` with the full org-beta asset body (`org_id`, `name`, `cloud_account`, `region`, `tags`).

**Expected:** `403` or `404` — never `200`, and no org-beta asset fields in the response.

**Observed:** `200 OK`, org-beta asset data fully disclosed to the org-alpha user.

**Notes:** The two accounts are genuinely separate organizations (the asset
carries `org_id: org-beta`, and org-alpha authenticates with its own
credentials). The test is intentionally left failing to track this bug.

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
