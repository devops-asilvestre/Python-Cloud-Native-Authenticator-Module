# CERT-US025-001 - PostgreSQL validation

## Result

**PASS** - all required records were found in PostgreSQL.

Validated records:

- `tenants`: tenant `01a1a77c-445c-75d0-b6bf-e16b56fc8b7c`, status `ACTIVE`;
- `identity_users`: user `01a1a77c-9b43-75ed-87d0-48fd7600d085`, status `ACTIVE`;
- `authentication_credentials`: credential
  `01a1a77c-d89d-7902-837e-91ff6060b913`, status `active`;
- `authentication_sessions`: session
  `01a1a77d-0b4b-7cee-a476-1a5338a9a8b9`, `active = true`;
- `authentication_audit`: `SessionCreated` and `AuthenticationSucceeded`
  records for the certified tenant and user.

No password or password hash is included in this evidence.
