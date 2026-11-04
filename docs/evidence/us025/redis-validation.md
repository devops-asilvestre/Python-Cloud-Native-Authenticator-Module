# CERT-US025-001 - Redis validation

## Result

**PASS** - the login session was cached in Redis.

| Field | Value |
|---|---|
| Key | `tenant:01a1a77c-445c-75d0-b6bf-e16b56fc8b7c:session:01a1a77d-0b4b-7cee-a476-1a5338a9a8b9` |
| Exists | `true` |
| Cached user | `01a1a77c-9b43-75ed-87d0-48fd7600d085` |
| Cached session | `active = true` |

The cached value contained creation and expiration timestamps and no secret
material.
