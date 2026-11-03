# US025 PostgreSQL Migration Validation

- **Data:** 2026-11-03
- **PostgreSQL:** PostgreSQL 17.11 on x86_64-pc-linux-musl
- **Container:** `docker-postgres-1` (healthy)

## Alembic

The Alembic environment now creates the async SQLAlchemy engine directly from
`DatabaseSettings.database_url`. The URL is no longer passed through
`Config.set_main_option()` or recovered with `Config.get_section()`, avoiding
`ConfigParser` interpolation of percent-encoded credentials.

### `alembic current`

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

Result: **passed**. The database was initially at base and connected without
the previous `ValueError`.

### `alembic upgrade head`

```text
INFO  [alembic.runtime.migration] Running upgrade  -> 20261103_001, Create tenant aggregate storage.
INFO  [alembic.runtime.migration] Running upgrade 20261103_001 -> 20261103_002, Identity Directory foundation.
INFO  [alembic.runtime.migration] Running upgrade 20261103_002 -> 20261103_003, Authentication foundation.
```

Result: **passed**.

### `alembic heads`

```text
20261103_003 (head)
```

### `alembic history`

```text
20261103_002 -> 20261103_003 (head), Authentication foundation.
20261103_001 -> 20261103_002, Identity Directory foundation.
<base> -> 20261103_001, Create tenant aggregate storage.
```

## PostgreSQL

### `\dt`

```text
 public | alembic_version            | table | authenticator
 public | authentication_audit       | table | authenticator
 public | authentication_credentials | table | authenticator
 public | authentication_sessions    | table | authenticator
 public | identity_users             | table | authenticator
 public | tenants                    | table | authenticator
```

### `SELECT * FROM alembic_version;`

```text
 version_num
-------------
 20261103_003
```

The tenant, identity, and authentication foundation tables are present.

## Quality validation

| Command | Result |
|---|---|
| `ruff check .` | Passed |
| `mypy --strict` | Passed |
| `pytest -q` | Passed: 193 tests |
| `python -m compileall src` | Passed |
