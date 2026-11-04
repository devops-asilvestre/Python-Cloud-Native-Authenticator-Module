# Authentication Service

**Bounded context:** Authentication & Assurance (core).

Responsabilidade: credenciais locais, verificação de autenticadores, controle de
tentativas, bloqueio temporário, sessões autenticadas e eventos de auditoria.
Segredos e material de verificação nunca devem ser publicados em eventos ou
logs.

A implementação está em
[`src/authentication_service`](../../src/authentication_service). O domínio é
independente de FastAPI, PostgreSQL, Redis e AWS; os repositórios e o publicador
de eventos são portas. O adaptador em memória existe para testes e
desenvolvimento local.

## Security invariants

- Passwords are validated by `PasswordPolicy` and stored only as Argon2id
  hashes (`PasswordHash`).
- Tenant scope is required by every application operation and repository key.
- Authentication failures return the same public error for an unknown email and
  an invalid password.
- Five consecutive failures lock a credential for 15 minutes by default.
- Sessions have a finite eight-hour lifetime by default and can be terminated
  explicitly.
- Domain events contain identifiers and outcome metadata only; no password or
  password hash is included.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).

The requirement-by-requirement acceptance matrix is maintained in
[`docs/user-stories/US025-authentication-foundation.md`](../../docs/user-stories/US025-authentication-foundation.md).
