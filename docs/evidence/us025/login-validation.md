# CERT-US025-001 - Login validation

## Result

**PASS** - valid login returned `HTTP 200` and created a session.

| Field | Value |
|---|---|
| Session ID | `01a1a77d-0b4b-7cee-a476-1a5338a9a8b9` |
| User ID | `01a1a77c-9b43-75ed-87d0-48fd7600d085` |
| Tenant ID | `01a1a77c-445c-75d0-b6bf-e16b56fc8b7c` |
| PostgreSQL state | `active = true` |
| Redis state | Session key present |

Additional event-generation checks also produced:

- invalid login: `HTTP 401`;
- valid login: `HTTP 200`;
- logout: `HTTP 204`.

Passwords are intentionally omitted from this evidence.
