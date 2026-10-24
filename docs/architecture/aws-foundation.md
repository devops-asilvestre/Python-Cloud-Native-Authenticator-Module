# AWS Foundation

This document defines the shared AWS foundation utilities for the platform.

## Design principles

- No direct `boto3.client(...)` calls from application code
- Centralized configuration with `pydantic-settings`
- Credential resolution through the AWS SDK default chain
- Contract-based service integration
- Health checks and connection validation before real workloads

## Architecture

Application -> AwsServiceContract -> AwsClientProvider -> AwsClientFactory -> boto3 -> AWS

## Local execution

The AWS session factory resolves credentials from the active environment,
shared config, or profile configuration. Nothing is hardcoded into source files.
