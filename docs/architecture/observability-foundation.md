# Observability Foundation

This document describes the shared observability foundation delivered as part of
US013. The package intentionally keeps the platform independent from concrete
telemetry backends while defining the contracts that every service must use.

## Layers

- Correlation and request identifiers
- Request and telemetry contexts
- Structured logger contracts
- Metric contracts
- Trace contracts
- Provider abstractions

## Architecture

Service -> Observability Contract -> Provider

The service layer references contracts, not concrete monitoring SDKs.
