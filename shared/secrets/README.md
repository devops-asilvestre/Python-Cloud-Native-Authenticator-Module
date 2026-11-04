# Secrets Management Foundation

This folder documents the shared secrets boundary. The Python implementation lives under `src/shared/secrets` and is exposed as `shared.secrets`.

The foundation is intentionally read-only and should only resolve secret values, metadata, and health status through a provider-backed abstraction.
