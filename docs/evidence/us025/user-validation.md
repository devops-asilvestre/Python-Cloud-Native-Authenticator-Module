# CERT-US025-001 - User validation

## Result

**PASS** - `POST /users` returned `HTTP 201` and user activation returned
`HTTP 200`.

| Field | Value |
|---|---|
| User ID | `01a1a77c-9b43-75ed-87d0-48fd7600d085` |
| Tenant ID | `01a1a77c-445c-75d0-b6bf-e16b56fc8b7c` |
| Type | `ADMIN` |
| Final status | `ACTIVE` |
| Email | `cert.retry@gmail.local` |

The user was created in PostgreSQL and activated before credential creation.
