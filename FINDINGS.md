# Findings

Confirmed defects surfaced by the test suite against the SecureVault API.
Each entry links to the test that reproduces it.

| ID | Severity | Title | Test | Status |
|----|----------|-------|------|--------|
| F-001 | Critical | Cross-org asset retrieval is not blocked | `tests/api/assets/test_asset_cross_org.py::test_cross_org_asset_retrieval_is_blocked` (TC-P1-01) | Open |

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
