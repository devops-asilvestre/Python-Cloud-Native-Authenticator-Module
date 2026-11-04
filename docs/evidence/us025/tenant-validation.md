# CERT-US025-001 - Tenant validation

## Result

**PASS** - `POST /tenants` returned `HTTP 201`, followed by activation with
`HTTP 200`.

| Field | Value |
|---|---|
| Tenant ID | `01a1a77c-445c-75d0-b6bf-e16b56fc8b7c` |
| Code | `C20261104135501` |
| Status | `ACTIVE` |
| Certification | `CERT-US025-001` |

The tenant was activated before creating the user because the authentication
foundation requires an active tenant context.
