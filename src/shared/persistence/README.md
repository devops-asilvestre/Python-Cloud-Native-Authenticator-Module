# Shared Persistence Foundation

This package provides the reusable PostgreSQL persistence foundation for the
platform. It intentionally keeps the domain and bounded contexts independent from
SQLAlchemy-specific implementation details while still exposing a small set of
practical infrastructure primitives.

## Responsibilities

- Database configuration and environment bindings
- Connection string and engine creation
- Async session lifecycle management
- Transaction and unit-of-work coordination
- Repository and async repository contracts
- Migration configuration helpers
- Tenant metadata propagation support through session info

## Architecture

Service or bounded context -> shared.persistence contracts -> SQLAlchemy adapter

The shared package does not contain business entities or domain repositories.
Concrete persistence implementations for each bounded context should live inside
that context's infrastructure layer and depend on these contracts.

## Multi-tenant foundation

The persistence layer exposes a `TenantContext` value object and stamps the
`tenant_id` on every created async session via `session.info`. This keeps tenant
scoping explicit without coupling the domain layer to SQLAlchemy details.

## Migration bootstrap

The project includes an Alembic scaffold under
[`src/shared/persistence/alembic`](./alembic/README.md) and a root
[`alembic.ini`](../../../alembic.ini). This creates the migration foundation the
platform needs before any bounded context adds concrete schema models.
