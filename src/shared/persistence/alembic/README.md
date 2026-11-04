# Alembic migration foundation

This directory provides the migration scaffold for the shared persistence layer.
The project keeps the migration metadata separate from each bounded context so
that platform-wide schema changes can be versioned in one reusable place.

## Usage

```bash
alembic -c alembic.ini revision --autogenerate -m "initial-schema"
alembic -c alembic.ini upgrade head
```

The migration environment reads connection settings from the shared database
configuration object, so every service inherits the same PostgreSQL defaults.
